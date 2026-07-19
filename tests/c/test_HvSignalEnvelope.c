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
#if HV_SIMD_NONE
    bIn = 1.0f;
#else
    for (int i=0; i<HV_N_SIMD; ++i) ((float *)&bIn)[i] = 1.0f;
#endif

    // Process 2 samples.
    // The first sample in a Hanning window has a weight of 0.0.
    // The second sample will have a non-zero weight.
    sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, NULL);
    sEnv_process((HeavyContextInterface *)&mockContext, &env, bIn, NULL);

    TEST_ASSERT_TRUE(env.accumulators[0] > 0.0f);
    TEST_ASSERT_EQUAL_INT(2, env.samplesSinceLastPeriod);

    sEnv_free(&env);
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_Envelope_Init);
    RUN_TEST(test_Envelope_IncrementalMath);
    return UNITY_END();
}
