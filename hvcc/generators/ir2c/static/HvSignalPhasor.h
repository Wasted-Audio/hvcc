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

#ifndef _HEAVY_SIGNAL_PHASOR_H_
#define _HEAVY_SIGNAL_PHASOR_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalPhasor {
#if HV_SIMD_AVX
  // As in all other variants, the phase is a 32-bit unsigned fixed-point number:
  // 0 .. 2^32 corresponds to 0 .. 1. Integer overflow wraps the phase exactly and
  // for free, also for negative frequencies (two's complement steps).
  // AVX (unlike AVX2) has no 256-bit integer instructions, so the 8 lanes are kept
  // as two halves (lanes 0-3 and 4-7) and computed with SSE2 integer instructions.
  // __hv_phasor_f() only uses phase[0], as the start phase of the next block
  // (broadcast to all 4 lanes); __hv_phasor_k_f() uses both halves.
  __m128i phase[2];
  __m128i inc; // __hv_phasor_k_f(): phase increment per block, 8 * step.s
#elif HV_SIMD_SSE
  __m128i phase;
  __m128i inc;
#elif HV_SIMD_NEON
  uint32x4_t phase;
  int32x4_t inc;
#else // HV_SIMD_NONE
  hv_uint32_t phase;
  hv_int32_t inc;
#endif
  union {
    float f2sc; // float to step conversion (used for __phasor~f)
    hv_int32_t s; // step value (used for __phasor_k~f)
  } step;
} SignalPhasor;

hv_size_t sPhasor_init(SignalPhasor *o, double samplerate);

hv_size_t sPhasor_k_init(SignalPhasor *o, float frequency, double samplerate);

void sPhasor_k_onMessage(HeavyContextInterface *_c, SignalPhasor *o, int letIn, const HvMessage *m);

void sPhasor_onMessage(HeavyContextInterface *_c, SignalPhasor *o, int letIn, const HvMessage *m);

#if HV_SIMD_AVX
// 32-bit fixed-point phase -> float in [0,1): the top 23 bits of the phase become the
// mantissa of a float with the exponent of 1.0, i.e. a value in [1,2), minus 1.
// (The former AVX version kept a float phase in [1,2) and wrapped it by forcing that
// exponent onto the sum. That maps x in [2,4) to x/2 instead of x-1, so half of the
// overshoot was lost at every wrap, e.g. 2.2 -> 1.1 instead of 1.2.)
static inline __m128 __hv_phasor_to_f_sse(__m128i p) {
  return _mm_sub_ps(_mm_castsi128_ps(_mm_or_si128(_mm_srli_epi32(p, 9), _mm_set1_epi32(0x3F800000))),
      _mm_set1_ps(1.0f));
}
#endif

static inline void __hv_phasor_f(SignalPhasor *o, hv_bInf_t bIn, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  // frequency per sample * 2^32/samplerate = phase step per sample, for each half
  const __m128 f2sc = _mm_set1_ps(o->step.f2sc);
  __m128i lo = _mm_cvtps_epi32(_mm_mul_ps(_mm256_castps256_ps128(bIn), f2sc)); // lanes 0-3
  __m128i hi = _mm_cvtps_epi32(_mm_mul_ps(_mm256_extractf128_ps(bIn, 1), f2sc)); // lanes 4-7
  // inclusive prefix sum within each half (two shift-and-add steps, as in the SSE
  // version): lane i holds the sum of the steps 0..i of its half
  lo = _mm_add_epi32(lo, _mm_slli_si128(lo, 4));
  lo = _mm_add_epi32(lo, _mm_slli_si128(lo, 8));
  hi = _mm_add_epi32(hi, _mm_slli_si128(hi, 4));
  hi = _mm_add_epi32(hi, _mm_slli_si128(hi, 8));
  // lanes 0-3 continue from the end of the previous block, lanes 4-7 from lane 3
  lo = _mm_add_epi32(o->phase[0], lo);
  hi = _mm_add_epi32(_mm_shuffle_epi32(lo, _MM_SHUFFLE(3,3,3,3)), hi);
  *bOut = _mm256_insertf128_ps(_mm256_castps128_ps256(__hv_phasor_to_f_sse(lo)), __hv_phasor_to_f_sse(hi), 1);
  // the last lane is the start phase of the next block
  o->phase[0] = _mm_shuffle_epi32(hi, _MM_SHUFFLE(3,3,3,3));
#elif HV_SIMD_SSE
  __m128i p = _mm_cvtps_epi32(_mm_mul_ps(bIn, _mm_set1_ps(o->step.f2sc))); // convert frequency to step
  p = _mm_add_epi32(p, _mm_slli_si128(p, 4)); // add incremental steps to phase (prefix sum)
  p = _mm_add_epi32(p, _mm_slli_si128(p, 8)); // http://stackoverflow.com/questions/10587598/simd-prefix-sum-on-intel-cpu?rq=1
  p = _mm_add_epi32(o->phase, p);
  *bOut = _mm_sub_ps(_mm_castsi128_ps(
      _mm_or_si128(_mm_srli_epi32(p, 9),
      _mm_set_epi32(0x3F800000, 0x3F800000, 0x3F800000, 0x3F800000))),
      _mm_set1_ps(1.0f));
  o->phase = _mm_shuffle_epi32(p, _MM_SHUFFLE(3,3,3,3));
#elif HV_SIMD_NEON
  int32x4_t p = vcvtq_s32_f32(vmulq_n_f32(bIn, o->step.f2sc));
  p = vaddq_s32(p, vextq_s32(vdupq_n_s32(0), p, 3)); // http://stackoverflow.com/questions/11259596/arm-neon-intrinsics-rotation
  p = vaddq_s32(p, vextq_s32(vdupq_n_s32(0), p, 2));
  uint32x4_t pp = vaddq_u32(o->phase, vreinterpretq_u32_s32(p));
  *bOut = vsubq_f32(vreinterpretq_f32_u32(vorrq_u32(vshrq_n_u32(pp, 9), vdupq_n_u32(0x3F800000))), vdupq_n_f32(1.0f));
  o->phase = vdupq_n_u32(pp[3]);
#else // HV_SIMD_NONE
  union { float f; hv_uint32_t u; } uphase;
  uphase.u = (o->phase >> 9) | 0x3F800000;
  *bOut = uphase.f - 1.0f;
  o->phase += ((int) (bIn * o->step.f2sc));
#endif
}

static inline void __hv_phasor_k_f(SignalPhasor *o, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  // the lanes hold p, p+s, ..., p+7s (see sPhasor_k_updatePhase()); each block adds 8s
  *bOut = _mm256_insertf128_ps(_mm256_castps128_ps256(
      __hv_phasor_to_f_sse(o->phase[0])), __hv_phasor_to_f_sse(o->phase[1]), 1);
  o->phase[0] = _mm_add_epi32(o->phase[0], o->inc);
  o->phase[1] = _mm_add_epi32(o->phase[1], o->inc);
#elif HV_SIMD_SSE
  *bOut = _mm_sub_ps(_mm_castsi128_ps(
      _mm_or_si128(_mm_srli_epi32(o->phase, 9),
      _mm_set_epi32(0x3F800000, 0x3F800000, 0x3F800000, 0x3F800000))),
      _mm_set1_ps(1.0f));
  o->phase = _mm_add_epi32(o->phase, o->inc);
#elif HV_SIMD_NEON
  *bOut = vsubq_f32(vreinterpretq_f32_u32(
      vorrq_u32(vshrq_n_u32(o->phase, 9),
      vdupq_n_u32(0x3F800000))),
      vdupq_n_f32(1.0f));
  o->phase = vaddq_u32(o->phase, vreinterpretq_u32_s32(o->inc));
#else // HV_SIMD_NONE
  union { float f; hv_uint32_t u; } uphase;
  uphase.u = (o->phase >> 9) | 0x3F800000;
  *bOut = uphase.f - 1.0f;
  o->phase += o->inc;
#endif
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_PHASOR_H_
