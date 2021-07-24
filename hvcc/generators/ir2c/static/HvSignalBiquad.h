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

#ifndef _HEAVY_SIGNAL_BIQUAD_H_
#define _HEAVY_SIGNAL_BIQUAD_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

// http://en.wikipedia.org/wiki/Digital_biquad_filter
typedef struct SignalBiquad {
#if HV_SIMD_NONE
  hv_bufferf_t xm1;
  hv_bufferf_t xm2;
#else
  hv_bufferf_t x;
#endif
  float ym1;
  float ym2;
} SignalBiquad;

hv_size_t sBiquad_init(SignalBiquad *o);

#if _WIN32 && !_WIN64
// NOTE(mhroth): unfortunately this specific definition of __hv_biquad_f for Win32 is necessary due to
// the limited stack and alignment capabilities of the VS compiler in this mode
#define __hv_biquad_f(o, bIn, bX0, bX1, bX2, bY1, bY2, bOut) __hv_biquad_f_win32(o, &bIn, &bX0, &bX1, &bX2, &bY1, &bY2, bOut)
void __hv_biquad_f_win32(SignalBiquad *o, hv_bInf_t *bIn, hv_bInf_t *bX0, hv_bInf_t *bX1, hv_bInf_t *bX2, hv_bInf_t *bY1, hv_bInf_t *bY2, hv_bOutf_t bOut);
#else
void __hv_biquad_f(SignalBiquad *o,
    hv_bInf_t bIn, hv_bInf_t bX0, hv_bInf_t bX1, hv_bInf_t bX2, hv_bInf_t bY1, hv_bInf_t bY2,
    hv_bOutf_t bOut);
#endif

typedef struct SignalBiquad_k {
#if HV_SIMD_AVX || HV_SIMD_SSE
  // preprocessed filter coefficients
  __m128 coeff_xp3;
  __m128 coeff_xp2;
  __m128 coeff_xp1;
  __m128 coeff_x0;
  __m128 coeff_xm1;
  __m128 coeff_xm2;
  __m128 coeff_ym1;
  __m128 coeff_ym2;

  // filter state
  __m128 xm1;
  __m128 xm2;
  __m128 ym1;
  __m128 ym2;
#elif HV_SIMD_NEON
  float32x4_t coeff_xp3;
  float32x4_t coeff_xp2;
  float32x4_t coeff_xp1;
  float32x4_t coeff_x0;
  float32x4_t coeff_xm1;
  float32x4_t coeff_xm2;
  float32x4_t coeff_ym1;
  float32x4_t coeff_ym2;
  float32x4_t xm1;
  float32x4_t xm2;
  float32x4_t ym1;
  float32x4_t ym2;
#else // HV_SIMD_NONE
  float xm1;
  float xm2;
  float ym1;
  float ym2;
#endif
  // original filter coefficients
  float b0; // x[0]
  float b1; // x[-1]
  float b2; // x[-2]
  float a1; // y[-1]
  float a2; // y[-2]
} SignalBiquad_k;

hv_size_t sBiquad_k_init(SignalBiquad_k *o, float x0, float x1, float x2, float y1, float y2);

void sBiquad_k_onMessage(SignalBiquad_k *o, int letIn, const HvMessage *m);

static inline void __hv_biquad_k_f(SignalBiquad_k *o, hv_bInf_t bIn, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  const __m128 c_xp3 = o->coeff_xp3;
  const __m128 c_xp2 = o->coeff_xp2;
  const __m128 c_xp1 = o->coeff_xp1;
  const __m128 c_x0 = o->coeff_x0;
  const __m128 c_xm1 = o->coeff_xm1;
  const __m128 c_xm2 = o->coeff_xm2;
  const __m128 c_ym1 = o->coeff_ym1;
  const __m128 c_ym2 = o->coeff_ym2;

  // lower half
  __m128 x3 = _mm_set1_ps(bIn[3]);
  __m128 x2 = _mm_set1_ps(bIn[2]);
  __m128 x1 = _mm_set1_ps(bIn[1]);
  __m128 x0 = _mm_set1_ps(bIn[0]);
  __m128 xm1 = o->xm1;
  __m128 xm2 = o->xm2;
  __m128 ym1 = o->ym1;
  __m128 ym2 = o->ym2;

  __m128 a = _mm_mul_ps(c_xp3, x3);
  __m128 b = _mm_mul_ps(c_xp2, x2);
  __m128 c = _mm_mul_ps(c_xp1, x1);
  __m128 d = _mm_mul_ps(c_x0, x0);
  __m128 e = _mm_mul_ps(c_xm1, xm1);
  __m128 f = _mm_mul_ps(c_xm2, xm2);
  __m128 g = _mm_mul_ps(c_ym1, ym1);
  __m128 h = _mm_mul_ps(c_ym2, ym2);

  __m128 i = _mm_add_ps(a, b);
  __m128 j = _mm_add_ps(c, d);
  __m128 k = _mm_add_ps(e, f);
  __m128 l = _mm_add_ps(g, h);
  __m128 m = _mm_add_ps(i, j);
  __m128 n = _mm_add_ps(k, l);

  __m128 lo_y = _mm_add_ps(m, n); // lower part of output buffer

  // upper half
  xm1 = x3;
  xm2 = x2;
  x3 = _mm_set1_ps(bIn[7]);
  x2 = _mm_set1_ps(bIn[6]);
  x1 = _mm_set1_ps(bIn[5]);
  x0 = _mm_set1_ps(bIn[4]);
  ym1 = _mm_set1_ps(lo_y[3]);
  ym2 = _mm_set1_ps(lo_y[2]);

  a = _mm_mul_ps(c_xp3, x3);
  b = _mm_mul_ps(c_xp2, x2);
  c = _mm_mul_ps(c_xp1, x1);
  d = _mm_mul_ps(c_x0, x0);
  e = _mm_mul_ps(c_xm1, xm1);
  f = _mm_mul_ps(c_xm2, xm2);
  g = _mm_mul_ps(c_ym1, ym1);
  h = _mm_mul_ps(c_ym2, ym2);

  i = _mm_add_ps(a, b);
  j = _mm_add_ps(c, d);
  k = _mm_add_ps(e, f);
  l = _mm_add_ps(g, h);
  m = _mm_add_ps(i, j);
  n = _mm_add_ps(k, l);

  __m128 up_y = _mm_add_ps(m, n); // upper part of output buffer

  o->xm1 = x3;
  o->xm2 = x2;
  o->ym1 = _mm_set1_ps(up_y[3]);
  o->ym2 = _mm_set1_ps(up_y[2]);

  *bOut = _mm256_insertf128_ps(_mm256_castps128_ps256(lo_y), up_y, 1);
#elif HV_SIMD_SSE
  __m128 x3 = _mm_shuffle_ps(bIn, bIn, _MM_SHUFFLE(3,3,3,3));
  __m128 x2 = _mm_shuffle_ps(bIn, bIn, _MM_SHUFFLE(2,2,2,2));
  __m128 x1 = _mm_shuffle_ps(bIn, bIn, _MM_SHUFFLE(1,1,1,1));
  __m128 x0 = _mm_shuffle_ps(bIn, bIn, _MM_SHUFFLE(0,0,0,0));

  __m128 a = _mm_mul_ps(o->coeff_xp3, x3);
  __m128 b = _mm_mul_ps(o->coeff_xp2, x2);
  __m128 c = _mm_mul_ps(o->coeff_xp1, x1);
  __m128 d = _mm_mul_ps(o->coeff_x0, x0);
  __m128 e = _mm_mul_ps(o->coeff_xm1, o->xm1);
  __m128 f = _mm_mul_ps(o->coeff_xm2, o->xm2);
  __m128 g = _mm_mul_ps(o->coeff_ym1, o->ym1);
  __m128 h = _mm_mul_ps(o->coeff_ym2, o->ym2);
  __m128 i = _mm_add_ps(a, b);
  __m128 j = _mm_add_ps(c, d);
  __m128 k = _mm_add_ps(e, f);
  __m128 l = _mm_add_ps(g, h);
  __m128 m = _mm_add_ps(i, j);
  __m128 n = _mm_add_ps(k, l);

  __m128 y = _mm_add_ps(m, n);

  o->xm1 = x3;
  o->xm2 = x2;
  o->ym1 = _mm_shuffle_ps(y, y, _MM_SHUFFLE(3,3,3,3));
  o->ym2 = _mm_shuffle_ps(y, y, _MM_SHUFFLE(2,2,2,2));

  *bOut = y;
#elif HV_SIMD_NEON
  float32x4_t x3 = vdupq_n_f32(bIn[3]);
  float32x4_t x2 = vdupq_n_f32(bIn[2]);
  float32x4_t x1 = vdupq_n_f32(bIn[1]);
  float32x4_t x0 = vdupq_n_f32(bIn[0]);

  float32x4_t a = vmulq_f32(o->coeff_xp3, x3);
  float32x4_t b = vmulq_f32(o->coeff_xp2, x2);
  float32x4_t c = vmulq_f32(o->coeff_xp1, x1);
  float32x4_t d = vmulq_f32(o->coeff_x0, x0);
  float32x4_t e = vmulq_f32(o->coeff_xm1, o->xm1);
  float32x4_t f = vmulq_f32(o->coeff_xm2, o->xm2);
  float32x4_t g = vmulq_f32(o->coeff_ym1, o->ym1);
  float32x4_t h = vmulq_f32(o->coeff_ym2, o->ym2);
  float32x4_t i = vaddq_f32(a, b);
  float32x4_t j = vaddq_f32(c, d);
  float32x4_t k = vaddq_f32(e, f);
  float32x4_t l = vaddq_f32(g, h);
  float32x4_t m = vaddq_f32(i, j);
  float32x4_t n = vaddq_f32(k, l);
  float32x4_t y = vaddq_f32(m, n);

  o->xm1 = x3;
  o->xm2 = x2;
  o->ym1 = vdupq_n_f32(y[3]);
  o->ym2 = vdupq_n_f32(y[2]);

  *bOut = y;
#else // HV_SIMD_NONE
  float y = o->b0*bIn + o->b1*o->xm1 + o->b2*o->xm2 - o->a1*o->ym1 - o->a2*o->ym2;
  o->xm2 = o->xm1;
  o->xm1 = bIn;
  o->ym2 = o->ym1;
  o->ym1 = y;
  *bOut = y;
#endif
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_BIQUAD_H_
