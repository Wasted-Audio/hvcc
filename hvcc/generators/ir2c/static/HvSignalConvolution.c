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

#include "HvSignalConvolution.h"

hv_size_t sConv_init(SignalConvolution *o, struct HvTable *table, const int size) {
  o->table = table;
  hv_size_t numBytes = hTable_init(&o->inputs, size);
  return numBytes;
}

void sConv_free(SignalConvolution *o) {
  o->table = NULL;
  hTable_free(&o->inputs);
}

void sConv_onMessage(HeavyContextInterface *_c, SignalConvolution *o, int letIndex,
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
        // convolution size should never exceed the coefficient table size
        hTable_resize(&o->inputs, (hv_uint32_t) msg_getFloat(m,0));
      }
      break;
    }
    default: return;
  }
}

static hv_bInf_t sConv_kernel(hv_bInf_t bIn, hv_bInf_t bInPrev, hv_bInf_t bInCoeff) {
#if HV_SIMD_AVX
  hv_assert(false & "There is no AVX implementation of __hv_conv_f");
  hv_bufferf_t d = _mm256_setzero_ps();
#elif HV_SIMD_SSE
  __m128 c0 = _mm_shuffle_ps(bInCoeff, bInCoeff, _MM_SHUFFLE(0,0,0,0));
  __m128 c1 = _mm_shuffle_ps(bInCoeff, bInCoeff, _MM_SHUFFLE(1,1,1,1));
  __m128 c2 = _mm_shuffle_ps(bInCoeff, bInCoeff, _MM_SHUFFLE(2,2,2,2));
  __m128 c3 = _mm_shuffle_ps(bInCoeff, bInCoeff, _MM_SHUFFLE(3,3,3,3));

  __m128 m0 = bIn;
  __m128 m2 = _mm_shuffle_ps(bInPrev, bIn, _MM_SHUFFLE(1,0,3,2));
  __m128 m1 = _mm_shuffle_ps(m2, bIn, _MM_SHUFFLE(2,1,2,1));
  __m128 m3 = _mm_shuffle_ps(bInPrev, m2, _MM_SHUFFLE(2,1,2,1));

  hv_bufferf_t a, b, c, d;
  __hv_mul_f(c0, m0, &a);
  __hv_fma_f(c1, m1, a, &b);
  __hv_fma_f(c2, m2, b, &c);
  __hv_fma_f(c3, m3, c, &d);
#elif HV_SIMD_NEON
  float32x4_t c0 = vdupq_lane_f32(vget_low_f32(bInCoeff), 0);
  float32x4_t c1 = vdupq_lane_f32(vget_low_f32(bInCoeff), 1);
  float32x4_t c2 = vdupq_lane_f32(vget_high_f32(bInCoeff), 0);
  float32x4_t c3 = vdupq_lane_f32(vget_high_f32(bInCoeff), 1);

  float32x4_t m0 = bIn;
  float32x4_t m1 = vextq_f32(bInPrev, bIn, 0x3);
  float32x4_t m2 = vextq_f32(bInPrev, bIn, 0x2);
  float32x4_t m3 = vextq_f32(bInPrev, bIn, 0x1);

  hv_bufferf_t a, b, c, d;
  __hv_mul_f(c0, m0, &a);
  __hv_fma_f(c1, m1, a, &b);
  __hv_fma_f(c2, m2, b, &c);
  __hv_fma_f(c3, m3, c, &d);
#else // HV_SIMD_NONE
  hv_bufferf_t d = bIn * bInCoeff;
#endif

  return d;
}

static inline int wrap(const int i, const int n) {
  if (i < 0) return (i+n);
  if (i >= n) return (i-n);
  return i;
}

void __hv_conv_f(SignalConvolution *o, hv_bInf_t bIn, hv_bOutf_t bOut) {
  hv_assert(o->table != NULL);
  float *const coeffs = hTable_getBuffer(o->table);
  hv_assert(coeffs != NULL);
  const int n = hTable_getSize(o->table); // length fir filter
  hv_assert((n&HV_N_SIMD_MASK) == 0); // n is a multiple of HV_N_SIMD

  float *const inputs = hTable_getBuffer(&o->inputs);
  hv_assert(inputs != NULL);
  const int m = hTable_getSize(&o->inputs); // length of input buffer.
  hv_assert(m >= n);
  const int h_orig = hTable_getHead(&o->inputs);

  hv_bufferf_t x0, out;
  x0 = bIn;
  __hv_zero_f(&out);

  int i = 0;
  int h = wrap(h_orig-HV_N_SIMD, m);
  for (; h >= 0; i+=HV_N_SIMD, h-=HV_N_SIMD) {
    hv_bufferf_t x1, c, o;
    __hv_load_f(inputs+h, &x1);
    __hv_load_f(coeffs+i, &c);
    o = sConv_kernel(x0, x1, c);
    __hv_add_f(o, out, &out);
    x0 = x1;
  }
  h += m; // h = m-HV_N_SIMD;
  for (; i < n; i+=HV_N_SIMD, h-=HV_N_SIMD) {
    hv_bufferf_t x1, c, o;
    __hv_load_f(inputs+h, &x1);
    __hv_load_f(coeffs+i, &c);
    o = sConv_kernel(x0, x1, c);
    __hv_add_f(o, out, &out);
    x0 = x1;
  }

  *bOut = out;

  __hv_store_f(inputs+h_orig, bIn); // store the new input to the inputs buffer
  hTable_setHead(&o->inputs, wrap(h_orig+HV_N_SIMD, m));
}
