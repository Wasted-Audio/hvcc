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

#ifndef _SIGNAL_LORENZ_H_
#define _SIGNAL_LORENZ_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalLorenz {
  float xm1;
  float ym1;
  float zm1;
} SignalLorenz;

hv_size_t sLorenz_init(SignalLorenz *o, float x, float y, float z);

// https://en.wikipedia.org/wiki/Lorenz_system#Overview
// x = x'+hstep*s*(y'-x')
// y = y'+hstep*(-x'*z'+r*x'-y')
// z = z'+hstep*(x'*y'-b*z')
static inline void __hv_lorenz_scalar_f(
    float xm1, float ym1, float zm1, float bInStep, float bInS, float bInR, float bInB,
    float *bOutX, float *bOutY, float *bOutZ) {
  *bOutX = hv_max_f(-100.0f, hv_min_f(xm1 + bInStep * bInS * (ym1 - xm1), 100.0f));
  *bOutY = hv_max_f(-100.0f, hv_min_f(ym1 + bInStep * (-xm1 * zm1 + (bInR * xm1) - ym1), 100.0f));
  *bOutZ = hv_max_f(-100.0f, hv_min_f(zm1 + bInStep * (xm1 * ym1 - bInB * zm1), 100.0f));
}

static inline void __hv_lorenz_f(SignalLorenz *o,
    hv_bInf_t bInStep, hv_bInf_t bInS, hv_bInf_t bInR, hv_bInf_t bInB,
    hv_bOutf_t bOutX, hv_bOutf_t bOutY, hv_bOutf_t bOutZ) {
#if HV_SIMD_AVX
  const float *const h = (float *) &bInStep;
  const float *const s = (float *) &bInS;
  const float *const r = (float *) &bInR;
  const float *const b = (float *) &bInB;

  float *const x = (float *) hv_alloca(3 * 8 * sizeof(float));
  float *const y = x + 8;
  float *const z = x + 16;

  __hv_lorenz_scalar_f(o->xm1, o->ym1, o->zm1, h[0], s[0], r[0], b[0], x, y, z);
  __hv_lorenz_scalar_f(x[0], y[0], z[0], h[1], s[1], r[1], b[1], x+1, y+1, z+1);
  __hv_lorenz_scalar_f(x[1], y[1], z[1], h[2], s[2], r[2], b[2], x+2, y+2, z+2);
  __hv_lorenz_scalar_f(x[2], y[2], z[2], h[3], s[3], r[3], b[3], x+3, y+3, z+3);
  __hv_lorenz_scalar_f(x[3], y[3], z[3], h[4], s[4], r[4], b[4], x+4, y+4, z+4);
  __hv_lorenz_scalar_f(x[4], y[4], z[4], h[5], s[5], r[5], b[5], x+5, y+5, z+5);
  __hv_lorenz_scalar_f(x[5], y[5], z[5], h[6], s[6], r[6], b[6], x+6, y+6, z+6);
  __hv_lorenz_scalar_f(x[6], y[6], z[6], h[7], s[7], r[7], b[7], x+7, y+7, z+7);

  o->xm1 = x[7];
  o->ym1 = y[7];
  o->zm1 = z[7];
  __hv_load_f(x, bOutX);
  __hv_load_f(y, bOutY);
  __hv_load_f(z, bOutZ);
#elif HV_SIMD_SSE
  const float *const h = (float *) &bInStep;
  const float *const s = (float *) &bInS;
  const float *const r = (float *) &bInR;
  const float *const b = (float *) &bInB;

  float *const x = (float *) hv_alloca(3 * 4 * sizeof(float));
  float *const y = x + 4;
  float *const z = x + 8;

  __hv_lorenz_scalar_f(o->xm1, o->ym1, o->zm1, h[0], s[0], r[0], b[0], x, y, z);
  __hv_lorenz_scalar_f(x[0], y[0], z[0], h[1], s[1], r[1], b[1], x+1, y+1, z+1);
  __hv_lorenz_scalar_f(x[1], y[1], z[1], h[2], s[2], r[2], b[2], x+2, y+2, z+2);
  __hv_lorenz_scalar_f(x[2], y[2], z[2], h[3], s[3], r[3], b[3], x+3, y+3, z+3);

  o->xm1 = x[3];
  o->ym1 = y[3];
  o->zm1 = z[3];
  __hv_load_f(x, bOutX);
  __hv_load_f(y, bOutY);
  __hv_load_f(z, bOutZ);
#elif HV_SIMD_NEON
  float *const x = (float *) hv_alloca(3 * 4 * sizeof(float));
  float *const y = x + 4;
  float *const z = x + 8;

  __hv_lorenz_scalar_f(o->xm1, o->ym1, o->zm1,
      vgetq_lane_f32(bInStep,0), vgetq_lane_f32(bInS,0), vgetq_lane_f32(bInR,0), vgetq_lane_f32(bInB,0),
      x, y, z);
  __hv_lorenz_scalar_f(x[0], y[0], z[0],
      vgetq_lane_f32(bInStep,1), vgetq_lane_f32(bInS,1), vgetq_lane_f32(bInR,1), vgetq_lane_f32(bInB,1),
      x+1, y+1, z+1);
  __hv_lorenz_scalar_f(x[1], y[1], z[1],
      vgetq_lane_f32(bInStep,2), vgetq_lane_f32(bInS,2), vgetq_lane_f32(bInR,2), vgetq_lane_f32(bInB,2),
      x+2, y+2, z+2);
  __hv_lorenz_scalar_f(x[2], y[2], z[2],
      vgetq_lane_f32(bInStep,3), vgetq_lane_f32(bInS,3), vgetq_lane_f32(bInR,3), vgetq_lane_f32(bInB,3),
      x+3, y+3, z+3);

  o->xm1 = x[3];
  o->ym1 = y[3];
  o->zm1 = z[3];
  __hv_load_f(x, bOutX);
  __hv_load_f(y, bOutY);
  __hv_load_f(z, bOutZ);
#else // HV_SIMD_NONE
  __hv_lorenz_scalar_f(o->xm1, o->ym1, o->zm1, bInStep, bInS, bInR, bInB, bOutX, bOutY, bOutZ);
  o->xm1 = *bOutX;
  o->ym1 = *bOutY;
  o->zm1 = *bOutZ;
#endif
}

void sLorenz_onMessage(HeavyContextInterface *_c, SignalLorenz *o, int letIndex,
    const HvMessage *m);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_LORENZ_H_
