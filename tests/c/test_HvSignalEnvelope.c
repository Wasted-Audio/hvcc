#include <stdio.h>
#include "unity.h"
#include "HvSignalEnvelope.h"
#include "mocks/HeavyMock.h"

void setUp(void) {
    mock_reset();
}

void tearDown(void) {
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

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_Envelope_Init);
    RUN_TEST(test_Envelope_IncrementalMath);
    return UNITY_END();
}
