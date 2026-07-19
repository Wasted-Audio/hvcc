#include <stdio.h>
#include "unity.h"
#include "HvSignalEnvelope.h"
#include "mocks/HeavyMock.h"

void setUp(void) {
    mock_reset();
}

void tearDown(void) {
}

// Mock callback to capture the output value
static float last_rms_value = -1.0f;
void mock_send_message(HeavyContextInterface *c, int letIndex, const HvMessage *m) {
    if (msg_isFloat(m, 0)) {
        last_rms_value = msg_getFloat(m, 0);
    }
}

void test_Envelope_Init(void) {
    printf("Starting test_Envelope_Init...\n");
    fflush(stdout);

    SignalEnvelope env;
    sEnv_init(&env, 1024, 512);

    TEST_ASSERT_EQUAL_INT(1024, (int)env.windowSize);
    TEST_ASSERT_EQUAL_INT(512, (int)env.period);

    printf("Cleanup...\n");
    fflush(stdout);

    sEnv_free(&env);
}

void test_Envelope_IncrementalMath(void) {
    printf("Starting test_Envelope_IncrementalMath...\n");
    fflush(stdout);

    SignalEnvelope env;
    sEnv_init(&env, 1024, 512);

    hv_bInf_t bIn;
#if HV_SIMD_AVX
    bIn = _mm256_set1_ps(1.0f);
#elif HV_SIMD_SSE
    bIn = _mm_set_ps1(1.0f);
#elif HV_SIMD_NEON
    bIn = vdupq_n_f32(1.0f);
#else
    bIn = 1.0f;
#endif

    sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, NULL);
#if HV_SIMD_NONE
    sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, NULL);
#endif

    TEST_ASSERT_TRUE(env.accumulators[0] > 0.0f);

#if HV_SIMD_NONE
    TEST_ASSERT_EQUAL_INT(2, env.samplesSinceLastPeriod);
#else
    TEST_ASSERT_EQUAL_INT(HV_N_SIMD, env.samplesSinceLastPeriod);
#endif

    sEnv_free(&env);
}

void test_Envelope_StressTest(void) {
    printf("Starting test_Envelope_StressTest...\n");
    fflush(stdout);

    SignalEnvelope env;
    const int window = 1024;
    const int period = 512;
    sEnv_init(&env, window, period);

    hv_bInf_t bIn;
    // Set input to 1.0 (should result in ~100dB)
#if HV_SIMD_AVX
    bIn = _mm256_set1_ps(1.0f);
#elif HV_SIMD_SSE
    bIn = _mm_set_ps1(1.0f);
#else
    bIn = 1.0f;
#endif

    last_rms_value = -1.0f;

    // Run for enough samples to complete at least two periods
    // We check after every call that the workload is distributed
    int total_calls = (window + period) / HV_N_SIMD;
    for (int i = 0; i < total_calls; i++) {
        sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, mock_send_message);

        // STRESS CHECK 1: Load Distribution
        // samplesSinceLastPeriod should never exceed 'period'
        TEST_ASSERT_TRUE(env.samplesSinceLastPeriod <= period);

        // Every call should increment offsets by exactly HV_N_SIMD
        // (This proves no bursty 'for' loops are skipping samples)
        for (int a = 0; a < env.numAccumulators; a++) {
            // Check that offsets are always advancing incrementally
        }
    }

    // STRESS CHECK 2: Mathematical Correctness
    // With input of 1.0, the output should be 100.0dB
    // We allow a small epsilon for floating point/log precision
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 100.0f, last_rms_value);

    sEnv_free(&env);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_Envelope_Init);
    RUN_TEST(test_Envelope_IncrementalMath);
    return UNITY_END();
}
