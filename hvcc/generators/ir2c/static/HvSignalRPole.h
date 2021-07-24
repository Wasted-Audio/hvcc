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

#ifndef _SIGNAL_RPOLE_H_
#define _SIGNAL_RPOLE_H_

#include "HvHeavyInternal.h"
#include "HvSignalDel1.h"

#ifdef __cplusplus
extern "C" {
#endif

// implements y[n] = x[n] - a*y[n-1]
// H(z) = 1/(1+a*z^-1)
typedef struct SignalRPole {
#if HV_SIMD_AVX
  SignalDel1 sDel1_fxiLN;
  SignalDel1 sDel1_kjkpV;
  SignalDel1 sDel1_dkIWc;
  SignalDel1 sDel1_bVeoW;
  SignalDel1 sDel1_PulZn;
  SignalDel1 sDel1_yTFig;
  SignalDel1 sDel1_Is9Qf;
  SignalDel1 sDel1_LIyNt;
  SignalDel1 sDel1_VqpU3;
  SignalDel1 sDel1_ZVYeg;
  SignalDel1 sDel1_IVAZh;
  SignalDel1 sDel1_F8WrY;
  SignalDel1 sDel1_rkFMy;
  SignalDel1 sDel1_BeqSK;
  hv_bufferf_t ym;
#elif HV_SIMD_SSE || HV_SIMD_NEON
  SignalDel1 sDel1_i8Twk;
  SignalDel1 sDel1_KYibU;
  SignalDel1 sDel1_spa5V;
  SignalDel1 sDel1_3HXdb;
  SignalDel1 sDel1_Aj1oK;
  SignalDel1 sDel1_jNX1g;
  hv_bufferf_t ym;
#else
  hv_bufferf_t ym;
#endif
} SignalRPole;

hv_size_t sRPole_init(SignalRPole *o);

void sRPole_onMessage(HeavyContextInterface *_c, SignalRPole *o, int letIn, const HvMessage *m);

static inline void __hv_rpole_f(SignalRPole *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_bufferf_t a, b, c, d, e, f, g, i, j, k, l, m, n;
  __hv_del1_f(&o->sDel1_fxiLN, bIn1, &a);
  __hv_mul_f(bIn1, a, &b);
  __hv_del1_f(&o->sDel1_kjkpV, a, &a);
  __hv_mul_f(b, a, &c);
  __hv_del1_f(&o->sDel1_dkIWc, a, &a);
  __hv_mul_f(c, a, &d);
  __hv_del1_f(&o->sDel1_bVeoW, a, &a);
  __hv_mul_f(d, a, &e);
  __hv_del1_f(&o->sDel1_PulZn, a, &a);
  __hv_mul_f(e, a, &f);
  __hv_del1_f(&o->sDel1_yTFig, a, &a);
  __hv_mul_f(f, a, &g);
  __hv_del1_f(&o->sDel1_Is9Qf, a, &a);
  __hv_mul_f(g, a, &a);
  __hv_del1_f(&o->sDel1_LIyNt, bIn0, &i);
  __hv_del1_f(&o->sDel1_VqpU3, i, &j);
  __hv_del1_f(&o->sDel1_ZVYeg, j, &k);
  __hv_del1_f(&o->sDel1_IVAZh, k, &l);
  __hv_del1_f(&o->sDel1_F8WrY, l, &m);
  __hv_del1_f(&o->sDel1_rkFMy, m, &n);
  __hv_mul_f(i, bIn1, &i);
  __hv_sub_f(bIn0, i, &i);
  __hv_fma_f(j, b, i, &i);
  __hv_mul_f(k, c, &c);
  __hv_sub_f(i, c, &c);
  __hv_fma_f(l, d, c, &c);
  __hv_mul_f(m, e, &e);
  __hv_sub_f(c, e, &e);
  __hv_fma_f(n, f, e, &e);
  __hv_del1_f(&o->sDel1_BeqSK, n, &n);
  __hv_mul_f(n, g, &g);
  __hv_sub_f(e, g, &g);
  __hv_fma_f(a, o->ym, g, &g);
  o->ym = g;
  *bOut = g;
#elif HV_SIMD_SSE || HV_SIMD_NEON
  hv_bufferf_t a, b, c, e, f;
  __hv_del1_f(&o->sDel1_i8Twk, bIn1, &a);
  __hv_mul_f(bIn1, a, &b);
  __hv_del1_f(&o->sDel1_KYibU, a, &a);
  __hv_mul_f(b, a, &c);
  __hv_del1_f(&o->sDel1_spa5V, a, &a);
  __hv_mul_f(c, a, &a);
  __hv_del1_f(&o->sDel1_3HXdb, bIn0, &e);
  __hv_del1_f(&o->sDel1_Aj1oK, e, &f);
  __hv_mul_f(e, bIn1, &e);
  __hv_sub_f(bIn0, e, &e);
  __hv_fma_f(f, b, e, &e);
  __hv_del1_f(&o->sDel1_jNX1g, f, &f);
  __hv_mul_f(f, c, &c);
  __hv_sub_f(e, c, &c);
  __hv_fma_f(a, o->ym, c, &c);
  o->ym = c;
  *bOut = c;
#else
  *bOut = bIn0 - bIn1 * o->ym;
  o->ym = *bOut;
#endif
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_RPOLE_H_
