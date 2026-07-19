/**
 * Copyright (c) 2014-2018 Enzien Audio Ltd.
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */

#include "HvSignalEnvelope.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846 // in case math.h doesn't include this defintion
#endif

static int ceilToNearestBlock(int x, int n) {
  return (int) (ceilf(((float) x) / ((float) n)) * n);
}

hv_size_t sEnv_init(SignalEnvelope *o, int windowSize, int period) {
  // Align to SIMD boundaries (always uses HV_N_SIMD even if HV_SIMD_NONE)
  o->windowSize = (windowSize <= HV_N_SIMD) ? HV_N_SIMD : (windowSize + (HV_N_SIMD - 1)) & ~(HV_N_SIMD - 1);
  o->period = (period <= HV_N_SIMD) ? HV_N_SIMD : (period > o->windowSize) ? o->windowSize : (period + (HV_N_SIMD - 1)) & ~(HV_N_SIMD - 1);

  o->numAccumulators = o->windowSize / o->period;
  o->samplesSinceLastPeriod = 0;
  hv_size_t numBytes = 0;

  // Allocate Hanning weights
  o->hanningWeights = (float *) hv_malloc(o->windowSize * sizeof(float));
  numBytes += o->windowSize * sizeof(float);

  // Calculate Normalised Hanning weights
  float hanningSum = 0.0f;
  for (int i = 0; i < o->windowSize; i++) {
    const float w = 0.5f * (1.0f - cosf(((float)(2.0 * M_PI * i)) / ((float)(o->windowSize - 1))));
    o->hanningWeights[i] = w;
    hanningSum += w;
  }
  for (int i = 0; i < o->windowSize; i++) o->hanningWeights[i] /= hanningSum;

  // Allocate Accumulators
  o->accumulators = (float *) hv_malloc(o->numAccumulators * sizeof(float));
  o->accOffsets = (int *) hv_malloc(o->numAccumulators * sizeof(int));
  numBytes += o->numAccumulators * (sizeof(float) + sizeof(int));

  for (int i = 0; i < o->numAccumulators; i++) {
    o->accumulators[i] = 0.0f;
    o->accOffsets[i] = -(i * o->period); // Offset cycles
  }

  return numBytes;
}

void sEnv_free(SignalEnvelope *o) {
  hv_free(o->hanningWeights);
  hv_free(o->accumulators);
  hv_free(o->accOffsets);
}

static void sEnv_sendMessage(HeavyContextInterface *_c, float sum,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  // finish RMS calculation. sqrt is removed as it can be combined with the log operation.
  // result is normalised such that 1 RMS == 100 dB
  float rms = (4.342944819032518f * hv_log_f(sum)) + 100.0f;

  // prepare the outgoing message. Schedule it at the beginning of the next block.
  HvMessage *const m = HV_MESSAGE_ON_STACK(1);

  msg_initWithFloat(m, hv_getCurrentSample(_c) + HV_N_SIMD, (rms < 0.0f) ? 0.0f : rms);
  hv_scheduleMessageForObject(_c, m, sendMessage, 0);
}

void sEnv_process(HeavyContextInterface *_c, SignalEnvelope *o, hv_bInf_t bIn,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
#if HV_SIMD_AVX
  // Square the 8-float input block
  __m256 bIn2 = _mm256_mul_ps(bIn, bIn);

  for (int a = 0; a < o->numAccumulators; a++) {
    if (o->accOffsets[a] >= 0) {
      // Load 8 Hanning weights (aligned)
      __m256 w = _mm256_load_ps(o->hanningWeights + o->accOffsets[a]);
      // Multiply weights by squared input
      __m256 prod = _mm256_mul_ps(bIn2, w);

      // Horizontal sum of the 8 floats in 'prod' and add to accumulator
      // Using the standard shuffle/add pattern for AVX horizontal sum
      __m128 lo = _mm256_castps256_ps128(prod);
      __m128 hi = _mm256_extractf128_ps(prod, 1);
      __m128 sum128 = _mm_add_ps(lo, hi);
      __m128 shuf = _mm_movehdup_ps(sum128);
      __m128 sum2 = _mm_add_ps(sum128, shuf);
      shuf = _mm_movehl_ps(shuf, sum2);
      __m128 final = _mm_add_ss(sum2, shuf);
      o->accumulators[a] += _mm_cvtss_f32(final);
    }
    o->accOffsets[a] += 8;
  }
  o->samplesSinceLastPeriod += 8;

#elif HV_SIMD_SSE
  // Square the 4-float input block
  __m128 bIn2 = _mm_mul_ps(bIn, bIn);

  for (int a = 0; a < o->numAccumulators; a++) {
    if (o->accOffsets[a] >= 0) {
      // Load 4 Hanning weights (aligned)
      __m128 w = _mm_load_ps(o->hanningWeights + o->accOffsets[a]);
      __m128 prod = _mm_mul_ps(bIn2, w);

      // Horizontal sum of the 4 floats in 'prod'
      __m128 shuf = _mm_movehdup_ps(prod);
      __m128 sum2 = _mm_add_ps(prod, shuf);
      shuf = _mm_movehl_ps(shuf, sum2);
      __m128 final = _mm_add_ss(sum2, shuf);
      o->accumulators[a] += _mm_cvtss_f32(final);
    }
    o->accOffsets[a] += 4;
  }
  o->samplesSinceLastPeriod += 4;
#elif HV_SIMD_NEON

#else // HV_SIMD_NONE
  const float bIn2 = bIn * bIn;

  for (int a = 0; a < o->numAccumulators; a++) {
    if (o->accOffsets[a] >= 0) {
      o->accumulators[a] += bIn2 * o->hanningWeights[o->accOffsets[a]];
    }
    o->accOffsets[a] += 1;
  }

  o->samplesSinceLastPeriod += 1;
#endif

  // Boundary check and message emission (Shared logic)
  if (o->samplesSinceLastPeriod >= o->period) {
    for (int a = 0; a < o->numAccumulators; a++) {
      if (o->accOffsets[a] >= o->windowSize) {
        sEnv_sendMessage(_c, o->accumulators[a], sendMessage);
        o->accumulators[a] = 0.0f;
        o->accOffsets[a] = 0;
      }
    }
    o->samplesSinceLastPeriod = 0;
  }
}
