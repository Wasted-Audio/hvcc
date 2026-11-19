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
  hv_bufferf_t xm1;
  hv_bufferf_t xm2;
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
  float xm1;
  float xm2;
  float ym1;
  float ym2;

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
  float y = o->b0*bIn + o->b1*o->xm1 + o->b2*o->xm2 - o->a1*o->ym1 - o->a2*o->ym2;
  o->xm2 = o->xm1;
  o->xm1 = bIn;
  o->ym2 = o->ym1;
  o->ym1 = y;
  *bOut = y;
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_BIQUAD_H_
