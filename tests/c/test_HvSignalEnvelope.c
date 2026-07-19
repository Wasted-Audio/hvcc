#include <stdio.h>
#include "unity.h"
#include "HvSignalEnvelope.h"
#include "mocks/HeavyMock.h"

void setUp(void) {
    mock_reset();
}

void tearDown(void) {
}

static hv_bInf_t hv_set_bInf(float f) {
    hv_bInf_t b;
#if HV_SIMD_AVX
    b = _mm256_set1_ps(f);
#elif HV_SIMD_SSE
    b = _mm_set_ps1(f);
#elif HV_SIMD_NEON
    b = vdupq_n_f32(f);
#else
    b = f;
#endif
    return b;
}

void test_Envelope_Init(void) {
    printf("Starting test_Envelope_Init...\n");
    fflush(stdout);
    
    SignalEnvelope env;
    sEnv_init(&env, 1024, 512);

    TEST_ASSERT_EQUAL_INT(1024, (int)env.windowSize);
    TEST_ASSERT_EQUAL_INT(512, (int)env.period);
    
    sEnv_free(&env);
}

void test_Envelope_IncrementalMath(void) {
    printf("Starting test_Envelope_IncrementalMath...\n");
    fflush(stdout);

    SignalEnvelope env;
    sEnv_init(&env, 1024, 512);
    
    hv_bInf_t bIn = hv_set_bInf(1.0f);
    
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

// Mock callback to capture the output value
static float last_rms_value = -1.0f;
void mock_send_message(HeavyContextInterface *c, int letIndex, const HvMessage *m) {
    if (msg_isFloat(m, 0)) {
        last_rms_value = msg_getFloat(m, 0);
    }
}

void test_Envelope_StressTest(void) {
    printf("Starting test_Envelope_StressTest...\n");
    fflush(stdout);

    SignalEnvelope env;
    const int window = 1024;
    const int period = 512;
    sEnv_init(&env, window, period);
    
    hv_bInf_t bIn = hv_set_bInf(1.0f);
    last_rms_value = -1.0f;

    // Run for enough samples to complete at least two periods
    int total_calls = (window + period) / HV_N_SIMD;
    for (int i = 0; i < total_calls; i++) {
        sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, mock_send_message);
        
        // Load Distribution Check
        TEST_ASSERT_TRUE(env.samplesSinceLastPeriod <= period);
    }

    // Mathematical Correctness Check
    // Constant input of 1.0 should result in ~100.0dB
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 100.0f, last_rms_value);

    sEnv_free(&env);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_Envelope_Init);
    RUN_TEST(test_Envelope_IncrementalMath);
    RUN_TEST(test_Envelope_StressTest);
    return UNITY_END();
}
