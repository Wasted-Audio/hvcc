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
  // 0 < BLOCK_SIZE <= period <= windowSize
  // NOTE(mhroth): this is an artificial limit, but it greatly simplifies development
  o->windowSize = (windowSize <= HV_N_SIMD) ? HV_N_SIMD : ceilToNearestBlock(windowSize, HV_N_SIMD);
  o->period = (period <= HV_N_SIMD) ? HV_N_SIMD : (period > o->windowSize) ? o->windowSize : ceilToNearestBlock(period, HV_N_SIMD);
  o->numSamplesInBuffer = 0;
  hv_size_t numBytes = 0;

  // allocate the signal buffer
  // the buffer is overdimensioned in this way (up to double), but not by much and so what
  const int bufferLength = 2 * o->windowSize;
  o->buffer = (float *) hv_malloc(bufferLength*sizeof(float));
  hv_assert(o->buffer != NULL);
  numBytes += bufferLength*sizeof(float);

  // allocate and calculate the hanning weights
  o->hanningWeights = (float *) hv_malloc(o->windowSize*sizeof(float));
  hv_assert(o->hanningWeights != NULL);
  numBytes += o->windowSize*sizeof(float);
  float hanningSum = 0.0f;
  for (int i = 0; i < o->windowSize; i++) {
    const float w = 0.5f * (1.0f - cosf(((float) (2.0 * M_PI * i)) / ((float) (o->windowSize - 1))));
    o->hanningWeights[i] = w;
    hanningSum += w;
  }
  for (int i = 0; i < o->windowSize; i++) {
    // normalise the hanning coefficients such that they represent a normalised weighted averaging
    o->hanningWeights[i] /= hanningSum;
  }

  return numBytes;
}

void sEnv_free(SignalEnvelope *o) {
  hv_free(o->hanningWeights);
  hv_free(o->buffer);
}

static void sEnv_sendMessage(HeavyContextInterface *_c, SignalEnvelope *o, float rms,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  // finish RMS calculation. sqrt is removed as it can be combined with the log operation.
  // result is normalised such that 1 RMS == 100 dB
  rms = (4.342944819032518f * hv_log_f(rms)) + 100.0f;

  // prepare the outgoing message. Schedule it at the beginning of the next block.
  HvMessage *const m = HV_MESSAGE_ON_STACK(1);

  msg_initWithFloat(m, hv_getCurrentSample(_c) + HV_N_SIMD, (rms < 0.0f) ? 0.0f : rms);
  hv_scheduleMessageForObject(_c, m, sendMessage, 0);

  hv_memcpy(o->buffer, o->buffer+o->period, sizeof(float)*(o->numSamplesInBuffer - o->period));
  o->numSamplesInBuffer -= o->period;
}

void sEnv_process(HeavyContextInterface *_c, SignalEnvelope *o, hv_bInf_t bIn,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
#if HV_SIMD_AVX
  _mm256_stream_ps(o->buffer+o->numSamplesInBuffer, _mm256_mul_ps(bIn,bIn)); // store bIn^2, no need to cache block
  o->numSamplesInBuffer += HV_N_SIMD;

  if (o->numSamplesInBuffer >= o->windowSize) {
    int n4 = o->windowSize & ~HV_N_SIMD_MASK;
    __m256 sum = _mm256_setzero_ps();
    while (n4) {
      __m256 x = _mm256_load_ps(o->buffer + n4 - HV_N_SIMD);
      __m256 h = _mm256_load_ps(o->hanningWeights + n4 - HV_N_SIMD);
      x = _mm256_mul_ps(x, h);
      sum = _mm256_add_ps(sum, x);
      n4 -= HV_N_SIMD;
    }
    sum = _mm256_hadd_ps(sum,sum); // horizontal sum
    sum = _mm256_hadd_ps(sum,sum);
    sEnv_sendMessage(_c, o, sum[0]+sum[4], sendMessage); // updates numSamplesInBuffer
  }
#elif HV_SIMD_SSE
  _mm_stream_ps(o->buffer+o->numSamplesInBuffer, _mm_mul_ps(bIn,bIn)); // store bIn^2, no need to cache block
  o->numSamplesInBuffer += HV_N_SIMD;

  if (o->numSamplesInBuffer >= o->windowSize) {
    int n4 = o->windowSize & ~HV_N_SIMD_MASK;
    __m128 sum = _mm_setzero_ps();
    while (n4) {
      __m128 x = _mm_load_ps(o->buffer + n4 - HV_N_SIMD);
      __m128 h = _mm_load_ps(o->hanningWeights + n4 - HV_N_SIMD);
      x = _mm_mul_ps(x, h);
      sum = _mm_add_ps(sum, x);
      n4 -= HV_N_SIMD;
    }
    sum = _mm_hadd_ps(sum,sum); // horizontal sum
    sum = _mm_hadd_ps(sum,sum);
    float f;
    _mm_store_ss(&f, sum);
    sEnv_sendMessage(_c, o, f, sendMessage);
  }
#elif HV_SIMD_NEON
  vst1q_f32(o->buffer+o->numSamplesInBuffer, vmulq_f32(bIn,bIn)); // store bIn^2, no need to cache block
  o->numSamplesInBuffer += HV_N_SIMD;

  if (o->numSamplesInBuffer >= o->windowSize) {
    int n4 = o->windowSize & ~HV_N_SIMD_MASK;
    float32x4_t sum = vdupq_n_f32(0.0f);
    while (n4) {
      float32x4_t x = vld1q_f32(o->buffer + n4 - HV_N_SIMD);
      float32x4_t h = vld1q_f32(o->hanningWeights + n4 - HV_N_SIMD);
      x = vmulq_f32(x, h);
      sum = vaddq_f32(sum, x);
      n4 -= HV_N_SIMD;
    }
    sEnv_sendMessage(_c, o, sum[0]+sum[1]+sum[2]+sum[3], sendMessage);
  }
#else // HV_SIMD_NONE
  o->buffer[o->numSamplesInBuffer] = (bIn*bIn);
  o->numSamplesInBuffer += HV_N_SIMD;

  if (o->numSamplesInBuffer >= o->windowSize) {
    float sum = 0.0f;
    for (int i = 0; i < o->windowSize; ++i) {
      sum += (o->hanningWeights[i] * o->buffer[i]);
    }
    sEnv_sendMessage(_c, o, sum, sendMessage);
  }
#endif
}
