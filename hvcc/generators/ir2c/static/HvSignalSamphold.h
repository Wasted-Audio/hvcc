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

#ifndef _SIGNAL_SAMPHOLD_H_
#define _SIGNAL_SAMPHOLD_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalSamphold {
  hv_bufferf_t s;
} SignalSamphold;

hv_size_t sSamphold_init(SignalSamphold *o);

static inline void __hv_samphold_f(SignalSamphold *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_assert(0); // __hv_samphold_f() not implemented
#elif HV_SIMD_SSE
  switch (_mm_movemask_ps(bIn1)) {
    default:
    case 0x0: *bOut = o->s; break;
    case 0x1: {
      *bOut = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(0,0,0,0));
      o->s = *bOut;
      break;
    }
    case 0x2: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(1,1,1,1));
      *bOut = _mm_blend_ps(o->s, x, 0xE);
      o->s = x;
      break;
    }
    case 0x3: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(1,1,1,1));
      *bOut = _mm_blend_ps(bIn0, x, 0xC);
      o->s = x;
      break;
    }
    case 0x4: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,2,2));
      *bOut = _mm_blend_ps(o->s, x, 0xC);
      o->s = x;
      break;
    }
    case 0x5: {
      *bOut = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,0,0));
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,2,2));
      break;
    }
    case 0x6: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,1,0));
      *bOut = _mm_blend_ps(o->s, x, 0xE);
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,2,2));
      break;
    }
    case 0x7: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(2,2,2,2));
      *bOut = _mm_blend_ps(bIn0, x, 0x8);
      o->s = x;
      break;
    }
    case 0x8: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      *bOut = _mm_blend_ps(o->s, x, 0x8);
      o->s = x;
      break;
    }
    case 0x9: {
      *bOut = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,0,0,0));
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xA: {
      const __m128 x = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,1,1,0));
      *bOut = _mm_blend_ps(o->s, x, 0xE);
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xB: {
      *bOut = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,1,1,0));
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xC: {
      *bOut = _mm_blend_ps(o->s, bIn0, 0xC);
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xD: {
      *bOut = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,2,0,0));
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xE: {
      *bOut = _mm_blend_ps(o->s, bIn0, 0xE);
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
    case 0xF: {
      *bOut = bIn0;
      o->s = _mm_shuffle_ps(bIn0, bIn0, _MM_SHUFFLE(3,3,3,3));
      break;
    }
  }
#elif HV_SIMD_NEON
  uint32x4_t mmA = vandq_u32(
      vreinterpretq_u32_f32(bIn1), (uint32x4_t) {0x1, 0x2, 0x4, 0x8}); // [0 1 2 3]
  uint32x4_t mmB = vextq_u32(mmA, mmA, 2);                             // [2 3 0 1]
  uint32x4_t mmC = vorrq_u32(mmA, mmB);                                // [0+2 1+3 0+2 1+3]
  uint32x4_t mmD = vextq_u32(mmC, mmC, 3);                             // [1+3 0+2 1+3 0+2]
  uint32x4_t mmE = vorrq_u32(mmC, mmD);                                // [0+1+2+3 ...]
  uint32_t movemask = vgetq_lane_u32(mmE, 0);
  switch (movemask) {
    default:
    case 0x0: *bOut = o->s; break;
    case 0x1: {
      *bOut = vdupq_n_f32(vgetq_lane_f32(bIn0,0));
      o->s = *bOut;
      break;
    }
    case 0x2: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,1));
      *bOut = vextq_f32(o->s, x, 3);
      o->s = x;
      break;
    }
    case 0x3: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,1));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0xFFFFFFFF, 0x0, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0x0, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF})));
      o->s = x;
      break;
    }
    case 0x4: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,2));
      *bOut = vextq_f32(o->s, x, 2);
      o->s = x;
      break;
    }
    case 0x5: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,0));
      const float32x4_t y = vdupq_n_f32(vgetq_lane_f32(bIn0,2));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(y), (uint32x4_t) {0x0, 0x0, 0xFFFFFFFF, 0xFFFFFFFF})));
      o->s = y;
    }
    case 0x6: {
      const float32x4_t y = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      float32x4_t z = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(o->s), (uint32x4_t) {0xFFFFFFFF, 0x0, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0x0, 0xFFFFFFFF, 0xFFFFFFFF, 0x0})));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(z), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(y), (uint32x4_t) {0x0, 0x0, 0x0, 0xFFFFFFFF})));
      o->s = y;
    }
    case 0x7: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,2));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0x0, 0x0, 0xFFFFFFFF, 0xFFFFFFFF})));
      o->s = x;
      break;
    }
    case 0x8: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      *bOut = vextq_f32(o->s, x, 1);
      o->s = x;
      break;
    }
    case 0x9: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,0));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0x0, 0x0, 0x0, 0xFFFFFFFF})));
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
    }
    case 0xA: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,1));
      const float32x4_t y = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      float32x4_t z = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(o->s), (uint32x4_t) {0xFFFFFFFF, 0x0, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0x0, 0xFFFFFFFF, 0xFFFFFFFF, 0x0})));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(z), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(y), (uint32x4_t) {0x0, 0x0, 0x0, 0xFFFFFFFF})));
      o->s = y;
    }
    case 0xB: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,1));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0x0, 0xFFFFFFFF}),
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0x0, 0x0, 0xFFFFFFFF, 0x0})));
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      break;
    }
    case 0xC: {
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(o->s), (uint32x4_t) {0xFFFFFFFF, 0xFFFFFFFF, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0x0, 0x0, 0xFFFFFFFF, 0xFFFFFFFF})));
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      break;
    }
    case 0xD: {
      const float32x4_t x = vdupq_n_f32(vgetq_lane_f32(bIn0,0));
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0xFFFFFFFF, 0x0, 0xFFFFFFFF, 0xFFFFFFFF}),
          vandq_u32(vreinterpretq_u32_f32(x), (uint32x4_t) {0x0, 0xFFFFFFFF, 0x0, 0x0})));
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
    }
    case 0xE: {
      *bOut = vreinterpretq_f32_u32(vorrq_u32(
          vandq_u32(vreinterpretq_u32_f32(o->s), (uint32x4_t) {0xFFFFFFFF, 0x0, 0x0, 0x0}),
          vandq_u32(vreinterpretq_u32_f32(bIn0), (uint32x4_t) {0x0, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF})));
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      break;
    }
    case 0xF: {
      *bOut = bIn0;
      o->s = vdupq_n_f32(vgetq_lane_f32(bIn0,3));
      break;
    }
  }
#else // HV_SIMD_NONE
  if (bIn1 != 0.0f) o->s = bIn0;
  *bOut = o->s;
#endif
}

void sSamphold_onMessage(HeavyContextInterface *_c, SignalSamphold *o, int letIndex,
    const HvMessage *m, void *sendMessage);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_SAMPHOLD_H_
