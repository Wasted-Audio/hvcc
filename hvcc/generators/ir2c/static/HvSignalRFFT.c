/**
 * Copyright (c) 2023 Wasted Audio
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

#include "HvSignalRFFT.h"
#include "pffft.h"

hv_size_t sRFFT_init(SignalRFFT *o, struct HvTable *table, const int size) {
  o->table = table;
  o->setup = pffft_new_setup(size, PFFFT_REAL);
  hv_size_t numBytes = hTable_init(&o->inputs, size);
  return numBytes;
}

void sRFFT_free(SignalRFFT *o) {
  o->table = NULL;
  hTable_free(&o->inputs);
}

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    case 1: {
      if (msg_isHashLike(m,0)) {
        HvTable *table = hv_table_get(_c, msg_getHash(m,0));
        if (table != NULL) {
          o->table = table;
          if (hTable_getSize(&o->inputs) != hTable_getSize(table)) {
            hTable_resize(&o->inputs,
                (hv_uint32_t) hv_min_ui(hTable_getSize(&o->inputs), hTable_getSize(table)));
          }
        }
      }
      break;
    }
    case 2: {
      if (msg_isFloat(m,0)) {
        // rfft size should never exceed the coefficient table size
        hTable_resize(&o->inputs, (hv_uint32_t) msg_getFloat(m,0));
      }
      break;
    }
    default: return;
  }
}


static inline int wrap(const int i, const int n) {
  if (i < 0) return (i+n);
  if (i >= n) return (i-n);
  return i;
}


void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  hv_assert(o->table != NULL);
  float *const work = hTable_getBuffer(o->table);
  hv_assert(work != NULL);
  const int n = hTable_getSize(o->table); // length fir filter
  hv_assert((n&HV_N_SIMD_MASK) == 0); // n is a multiple of HV_N_SIMD

  float *const inputs = hTable_getBuffer(&o->inputs);
  hv_assert(inputs != NULL);
  const int m = hTable_getSize(&o->inputs); // length of input buffer.
  hv_assert(m >= n);
  const int h_orig = hTable_getHead(&o->inputs);

  float *const bOut = (float *)(hv_alloca(2*n*sizeof(float)));

  pffft_transform_ordered(o->setup, &bIn, bOut, work, PFFFT_FORWARD);

  // uninterleave result into the output buffers
  #if HV_SIMD_SSE || HV_SIMD_AVX
  for (int i = 0, j = 0; j < n; j += 4, i += 8) {
    __m128 a = _mm_load_ps(bOut+i);                // LRLR
    __m128 b = _mm_load_ps(bOut+4+i);              // LRLR
    __m128 x = _mm_shuffle_ps(a, b, _MM_SHUFFLE(2,0,2,0)); // LLLL
    __m128 y = _mm_shuffle_ps(a, b, _MM_SHUFFLE(3,1,3,1)); // RRRR
    _mm_store_ps(bOut0+j, x);
    _mm_store_ps(bOut1+j, y);
  }
  #elif HV_SIMD_NEON
  for (int i = 0, j = 0; j < n; j += 4, i += 8) {
    float32x4x2_t a = vld2q_f32(bOut+i); // load and uninterleave
    vst1q_f32(bOut0+j, a.val[0]);
    vst1q_f32(bOut1+j, a.val[1]);
  }
  #else // HV_SIMD_NONE
  for (int j = 0; j < n; ++j) {
    bOut0[n+j] = bOut[0+2*j];
    bOut1[n+j] = bOut[1+2*j];
  }
  #endif

  __hv_store_f(inputs+h_orig, bIn); // store the new input to the inputs buffer
  hTable_setHead(&o->inputs, wrap(h_orig+HV_N_SIMD, m));
}


void __hv_rifft_f(SignalRFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  hv_assert(o->table != NULL);
  float *const work = hTable_getBuffer(o->table);
  hv_assert(work != NULL);
  const int n = hTable_getSize(o->table); // length fir filter
  hv_assert((n&HV_N_SIMD_MASK) == 0); // n is a multiple of HV_N_SIMD

  float *const inputs = hTable_getBuffer(&o->inputs);
  hv_assert(inputs != NULL);
  const int m = hTable_getSize(&o->inputs); // length of input buffer.
  hv_assert(m >= n);
  const int h_orig = hTable_getHead(&o->inputs);

  float *const bIn = (float *)(hv_alloca(2*n*sizeof(float)));

  // interleave the input buffers into the transform buffer
  #if HV_SIMD_AVX
  for (int i = 0, j = 0; j < n; j += 8, i += 16) {
    __m256 x = _mm256_load_ps(bIn0);    // LLLLLLLL
    __m256 y = _mm256_load_ps(bIn1); // RRRRRRRR
    __m256 a = _mm256_unpacklo_ps(x, y);  // LRLRLRLR
    __m256 b = _mm256_unpackhi_ps(x, y);  // LRLRLRLR
    _mm256_store_ps(bIn+i, a);
    _mm256_store_ps(bIn+8+i, b);
  }
  #elif HV_SIMD_SSE
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    __m128 x = _mm_load_ps(bIn0);    // LLLL
    __m128 y = _mm_load_ps(bIn1); // RRRR
    __m128 a = _mm_unpacklo_ps(x, y);  // LRLR
    __m128 b = _mm_unpackhi_ps(x, y);  // LRLR
    _mm_store_ps(bIn+i, a);
    _mm_store_ps(bIn+4+i, b);
  }
  #elif HV_SIMD_NEON
  // https://community.arm.com/groups/processors/blog/2012/03/13/coding-for-neon--part-5-rearranging-vectors
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    float32x4_t x = vld1q_f32(bIn0);
    float32x4_t y = vld1q_f32(bIn1);
    float32x4x2_t z = {x, y};
    vst2q_f32(bIn+i, z); // interleave and store
  }
  #else // HV_SIMD_NONE
  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < n; ++j) {
      bIn[0+2*j] = bIn0[n+j];
      bIn[1+2*j] = bIn1[n+j];
    }
  }
  #endif

  pffft_transform_ordered(o->setup, bIn, &bOut, work, PFFFT_BACKWARD);

  // __hv_store_f(inputs+h_orig, bIn); // store the new input to the inputs buffer
  hTable_setHead(&o->inputs, wrap(h_orig+HV_N_SIMD, m));
}
