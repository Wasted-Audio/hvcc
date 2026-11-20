#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "unity.h"
#include "HvSignalEnvelope.h"
#include "mocks/HeavyMock.h"

/* ---------------------------------------------------------------------------
 * Build identity
 * ------------------------------------------------------------------------ */

#define HV_STR_(x) #x
#define HV_STR(x) HV_STR_(x)

#if HV_SIMD_AVX
#define SIMD_NAME "AVX"
#elif HV_SIMD_SSE
#define SIMD_NAME "SSE"
#elif HV_SIMD_NEON
#define SIMD_NAME "NEON"
#else
#define SIMD_NAME "NONE"
#endif
#define SIMD_TAG SIMD_NAME "/" HV_STR(HV_N_SIMD)

/* ---------------------------------------------------------------------------
 * Config table
 *
 * Every value is a multiple of the widest block we build (8, AVX), so the same
 * table is meaningful for NONE/SSE/NEON/AVX.
 * ------------------------------------------------------------------------ */

typedef struct {
    const char *name;
    int window;
    int period;
    const char *why;
} EnvConfig;

static const EnvConfig CONFIGS[] = {
    {"w1024_p512",   1024,  512, "baseline, 2 accumulators"},
    {"w1024_p128",   1024,  128, "8 accumulators, offsets cycle"},
    {"w1024_p1024",  1024, 1024, "single accumulator, one emission per window"},
    {"w2048_p256",   2048,  256, "long window, many accumulators"},
    {"w256_p64",      256,   64, "small window, well above SIMD minimum"},
    {"w1024_p300",   1024,  300, "period does not divide window (regression)"},
};
#define N_CONFIGS (sizeof(CONFIGS) / sizeof(CONFIGS[0]))

/* ---------------------------------------------------------------------------
 * Soft assertions.
 *
 * Unity's TEST_ASSERT_* abort the test case, so a failure in config 0 would
 * hide configs 1..n. These collect instead, and name the config that broke.
 * ------------------------------------------------------------------------ */

typedef struct {
    const char *config;
    int failures;
} ExpectCtx;

static int expect_int(ExpectCtx *c, const char *what, long got, long want) {
    if (got == want) return 0;
    printf("  FAIL [%s] %s: got %ld, want %ld\n", c->config, what, got, want);
    c->failures++;
    return 1;
}

static int expect_near(ExpectCtx *c, const char *what, double got, double want, double tol) {
    const double err = fabs(got - want);
    const double limit = tol + tol * fabs(want);
    if (err <= limit) return 0;
    printf("  FAIL [%s] %s: got %.6f, want %.6f (err %.6g > %.6g)\n",
           c->config, what, got, want, err, limit);
    c->failures++;
    return 1;
}

/* ---------------------------------------------------------------------------
 * Signal helpers
 * ------------------------------------------------------------------------ */

#define BLOCK HV_N_SIMD

static hv_bInf_t block_from(const float *v) {
    hv_bInf_t b;
#if HV_SIMD_AVX
    b = _mm256_set_ps(v[7], v[6], v[5], v[4], v[3], v[2], v[1], v[0]);
#elif HV_SIMD_SSE
    b = _mm_set_ps(v[3], v[2], v[1], v[0]);
#elif HV_SIMD_NEON
    b = vld1q_f32(v);
#else
    b = v[0];
#endif
    return b;
}

/* Deterministic noise in [-1, 1). Identical for every SIMD variant, so the
 * reference below is comparable across builds. */
static uint32_t lcg_state;
static float next_sample(void) {
    lcg_state = lcg_state * 1664525u + 1013904223u;
    return (float) ((int32_t) lcg_state) / 2147483648.0f;   /* [-1, 1) */
}

/* Independent scalar evaluation of what the envelope should report for a
 * window ending at sample index `end`: 10*log10( sum w[i]*x[end-win+i]^2 ). */
static double reference_db(const float *x, int end, const float *w, int win) {
    double acc = 0.0;
    for (int i = 0; i < win; i++) {
        const double s = (double) x[end - win + i];
        acc += s * s * (double) w[i];
    }
    return 10.0 * log10(acc) + 100.0;   /* matches sEnv_sendMessage */
}

/* ---------------------------------------------------------------------------
 * Message capture
 * ------------------------------------------------------------------------ */

#define CAP 64

static hv_uint32_t msg_ts[CAP];
static int msg_outlet[CAP];
static double msg_db[CAP];
static int n_msg;

static void capture_message(HeavyContextInterface *_c, int outlet, const HvMessage *m) {
    (void) _c;
    if (n_msg >= CAP) return;                     /* the count assertion catches this */
    msg_ts[n_msg] = msg_getTimestamp(m);
    msg_outlet[n_msg] = outlet;
    msg_db[n_msg] = msg_isFloat(m, 0) ? (double) msg_getFloat(m, 0) : -1.0;
    n_msg++;
}

static void reset_capture(void) {
    memset(msg_ts, 0, sizeof(msg_ts));
    memset(msg_outlet, 0, sizeof(msg_outlet));
    memset(msg_db, 0, sizeof(msg_db));
    n_msg = 0;
}

void setUp(void) {
    mock_reset();
    reset_capture();
    lcg_state = 0x12345678u;
}

void tearDown(void) {}

static int round_up(int x, int n) { return ((x + n - 1) / n) * n; }

/* ---------------------------------------------------------------------------
 * Test 1: init contract, per config
 * ------------------------------------------------------------------------ */

static int check_init(ExpectCtx *ctx, const EnvConfig *cfg) {
    SignalEnvelope env;
    const int n = HV_N_SIMD;

    const hv_size_t bytes = sEnv_init(&env, cfg->window, cfg->period);

    /* Rounded up to a block boundary, never down. */
    const int want_window = cfg->window <= n ? n : round_up(cfg->window, n);
    const int want_period = cfg->period <= n ? n
                          : cfg->period > want_window ? want_window
                          : round_up(cfg->period, n);

    ctx->failures += expect_int(ctx, "windowSize", env.windowSize, want_window);
    ctx->failures += expect_int(ctx, "period", env.period, want_period);
    ctx->failures += expect_int(ctx, "period <= windowSize",
                                env.period <= env.windowSize, 1);
    ctx->failures += expect_int(ctx, "windowSize % N", env.windowSize % n, 0);
    ctx->failures += expect_int(ctx, "period % N", env.period % n, 0);
    ctx->failures += expect_int(ctx, "numAccumulators", env.numAccumulators,
                                (env.windowSize + env.period - 1) / env.period);

    /* Hanning window: normalised, non-negative, zero at both ends. */
    double sum = 0.0;
    int negative = 0;
    for (int i = 0; i < env.windowSize; i++) {
        sum += env.hanningWeights[i];
        if (env.hanningWeights[i] < 0.0f) negative = 1;
    }
    ctx->failures += expect_near(ctx, "hanning sum", sum, 1.0, 1e-5);
    ctx->failures += expect_int(ctx, "negative weights", negative, 0);
    ctx->failures += expect_near(ctx, "w[0]", env.hanningWeights[0], 0.0, 1e-6);
    ctx->failures += expect_near(ctx, "w[last]", env.hanningWeights[env.windowSize - 1], 0.0, 1e-6);

    /* Peak of a Hanning window sits at the centre. */
    int argmax = 0;
    for (int i = 1; i < env.windowSize; i++)
        if (env.hanningWeights[i] > env.hanningWeights[argmax]) argmax = i;
    ctx->failures += expect_int(ctx, "argmax near centre",
                                abs(argmax - env.windowSize / 2) <= 1, 1);

    /* Return value must cover everything the object allocates. */
    const hv_size_t want_bytes = (hv_size_t) env.windowSize * sizeof(float)
        + (hv_size_t) env.numAccumulators * (sizeof(float) + sizeof(int));
    ctx->failures += expect_int(ctx, "numBytes", (long) bytes, (long) want_bytes);

    sEnv_free(&env);
    return ctx->failures;
}

void test_Envelope_Init(void) {
    ExpectCtx ctx = {"init", 0};
    for (size_t i = 0; i < N_CONFIGS; i++) {
        ctx.config = CONFIGS[i].name;
        check_init(&ctx, &CONFIGS[i]);
    }
    TEST_ASSERT_EQUAL_INT_MESSAGE(0, ctx.failures, "init contract violated");
}

/* ---------------------------------------------------------------------------
 * Test 2: incremental accumulation is exact after one block
 * ------------------------------------------------------------------------ */

static int check_incremental(ExpectCtx *ctx, const EnvConfig *cfg) {
    SignalEnvelope env;
    sEnv_init(&env, cfg->window, cfg->period);
    reset_capture();

    const float ones[8] = {1, 1, 1, 1, 1, 1, 1, 1};
    mockContext.currentSample = 0;
    sEnv_process((HeavyContextInterface *) &mockContext, &env, block_from(ones), capture_message);

    /* Accumulator 0 covers the first `windowSize` samples of the window, so
     * after one block it must equal the sum of the first HV_N_SIMD weights. */
    double want = 0.0;
    for (int i = 0; i < HV_N_SIMD; i++) want += env.hanningWeights[i];
    ctx->failures += expect_near(ctx, "accumulators[0] after 1 block",
                                 env.accumulators[0], want, 1e-6);

    /* Accumulators that have not been reached yet must still be zero. */
    for (int a = 1; a < env.numAccumulators; a++) {
        if (env.accOffsets[a] < 0) {
            char label[64];
            snprintf(label, sizeof label, "accumulators[%d] before start", a);
            ctx->failures += expect_near(ctx, label, env.accumulators[a], 0.0, 1e-9);
        }
    }

    ctx->failures += expect_int(ctx, "samplesSinceLastPeriod",
                                env.samplesSinceLastPeriod, HV_N_SIMD);
    ctx->failures += expect_int(ctx, "no message before window filled", n_msg, 0);

    sEnv_free(&env);
    return ctx->failures;
}

void test_Envelope_IncrementalMath(void) {
    ExpectCtx ctx = {"incremental", 0};
    for (size_t i = 0; i < N_CONFIGS; i++) {
        ctx.config = CONFIGS[i].name;
        check_incremental(&ctx, &CONFIGS[i]);
    }
    TEST_ASSERT_EQUAL_INT_MESSAGE(0, ctx.failures, "accumulation is not exact");
}

/* ---------------------------------------------------------------------------
 * Test 3: level and cadence against a scalar reference
 * ------------------------------------------------------------------------ */

#define N_EMIT 4

static int check_signal(ExpectCtx *ctx, const EnvConfig *cfg) {
    SignalEnvelope env;
    sEnv_init(&env, cfg->window, cfg->period);
    reset_capture();

    const int win = env.windowSize;
    const int per = env.period;
    const int n_samples = win + (N_EMIT - 1) * per;
    float *x = (float *) calloc((size_t) n_samples, sizeof(float));
    TEST_ASSERT_NOT_NULL(x);

    /* Generate first, so the reference never depends on the processing order. */
    lcg_state = 0x12345678u;
    for (int i = 0; i < n_samples; i++) x[i] = next_sample();

    for (int i = 0; i < n_samples; i += BLOCK) {
        mockContext.currentSample = (hv_uint32_t) i;
        sEnv_process((HeavyContextInterface *) &mockContext, &env,
                     block_from(&x[i]), capture_message);
    }

    ctx->failures += expect_int(ctx, "messages emitted", n_msg, N_EMIT);

    for (int e = 0; e < n_msg && e < N_EMIT; e++) {
        char label[96];

        /* First emission lands when the window is full; then one per period. */
        const int want_ts = win + e * per;
        snprintf(label, sizeof label, "msg[%d] timestamp", e);
        ctx->failures += expect_int(ctx, label, (long) msg_ts[e], want_ts);

        snprintf(label, sizeof label, "msg[%d] outlet", e);
        ctx->failures += expect_int(ctx, label, msg_outlet[e], 0);

        /* Levels must match the windowed RMS at that sample, computed in
         * double from the same input. 1e-3 dB is ~0.02 % in amplitude. */
        snprintf(label, sizeof label, "msg[%d] level", e);
        ctx->failures += expect_near(ctx, label, msg_db[e],
                                     reference_db(x, want_ts, env.hanningWeights, win),
                                     1e-3);
    }

    free(x);
    sEnv_free(&env);
    return ctx->failures;
}

void test_Envelope_SignalAndCadence(void) {
    ExpectCtx ctx = {"signal", 0};
    for (size_t i = 0; i < N_CONFIGS; i++) {
        ctx.config = CONFIGS[i].name;
        check_signal(&ctx, &CONFIGS[i]);
    }
    TEST_ASSERT_EQUAL_INT_MESSAGE(0, ctx.failures, "level or cadence wrong");
}

/* ---------------------------------------------------------------------------
 * Test 4: degenerate input does not produce NaN
 * ------------------------------------------------------------------------ */

void test_Envelope_ConstantIsMinusInfinity(void) {
    /* All-zero input gives a zero window sum, which must clamp to 0 dB and not
     * emit NaN/inf. Protects the (rms < 0.0f) ? 0 : rms path. */
    SignalEnvelope env;
    sEnv_init(&env, 1024, 512);
    reset_capture();

    const float zeros[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    for (int i = 0; i < 1024; i += BLOCK) {
        mockContext.currentSample = (hv_uint32_t) i;
        sEnv_process((HeavyContextInterface *) &mockContext, &env,
                     block_from(zeros), capture_message);
    }

    TEST_ASSERT_EQUAL_INT(1, n_msg);
    TEST_ASSERT_FALSE(isnan(msg_db[0]));
    TEST_ASSERT_TRUE(msg_db[0] >= -1e-6);

    sEnv_free(&env);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_Envelope_Init);
    RUN_TEST(test_Envelope_IncrementalMath);
    RUN_TEST(test_Envelope_SignalAndCadence);
    RUN_TEST(test_Envelope_ConstantIsMinusInfinity);
    return UNITY_END();
}
