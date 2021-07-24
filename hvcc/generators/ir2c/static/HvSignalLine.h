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

#ifndef _SIGNAL_LINE_H_
#define _SIGNAL_LINE_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalLine {
#if HV_SIMD_AVX
  __m128i n; // remaining samples to target
#else
  hv_bufferi_t n; // remaining samples to target
#endif
  hv_bufferf_t x; // current output
  hv_bufferf_t m; // increment
  hv_bufferf_t t; // target value
} SignalLine;

hv_size_t sLine_init(SignalLine *o);

static inline void __hv_line_f(SignalLine *o, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  __m128i n = o->n;
  __m128i masklo = _mm_cmplt_epi32(n, _mm_setzero_si128()); // n < 0
  n = _mm_sub_epi32(n, _mm_set1_epi32(4)); // subtract HV_N_SIMD from remaining samples
  __m128i maskhi = _mm_cmplt_epi32(n, _mm_setzero_si128());
  o->n = _mm_sub_epi32(n, _mm_set1_epi32(4));
  __m256 mask = _mm256_insertf128_ps(_mm256_castps128_ps256(_mm_castsi128_ps(masklo)), _mm_castsi128_ps(maskhi), 1);

  __m256 x = o->x;
  *bOut = _mm256_or_ps(_mm256_and_ps(mask, o->t), _mm256_andnot_ps(mask, x));

  // add slope from sloped samples
  o->x = _mm256_add_ps(x, o->m);
#elif HV_SIMD_SSE
  __m128i n = o->n;
  __m128 mask = _mm_castsi128_ps(_mm_cmplt_epi32(n, _mm_setzero_si128())); // n < 0

  __m128 x = o->x;
  *bOut = _mm_or_ps(_mm_and_ps(mask, o->t), _mm_andnot_ps(mask, x));

  // subtract HV_N_SIMD from remaining samples
  o->n = _mm_sub_epi32(n, _mm_set1_epi32(HV_N_SIMD));

  // add slope from sloped samples
  o->x = _mm_add_ps(x, o->m);
#elif HV_SIMD_NEON
  int32x4_t n = o->n;
  int32x4_t mask = vreinterpretq_s32_u32(vcltq_s32(n, vdupq_n_s32(0)));
  float32x4_t x = o->x;
  *bOut = vreinterpretq_f32_s32(vorrq_s32(
      vandq_s32(mask, vreinterpretq_s32_f32(o->t)),
      vbicq_s32(vreinterpretq_s32_f32(x), mask)));
  o->n = vsubq_s32(n, vdupq_n_s32(HV_N_SIMD));
  o->x = vaddq_f32(x, o->m);
#else // HV_SIMD_NONE
  *bOut = (o->n < 0) ? o->t : o->x;
  o->n -= HV_N_SIMD;
  o->x += o->m;
#endif
}

void sLine_onMessage(HeavyContextInterface *_c, SignalLine *o, int letIndex,
    const HvMessage *m, void *sendMessage);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_LINE_H_
