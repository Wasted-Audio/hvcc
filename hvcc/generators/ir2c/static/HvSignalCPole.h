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

#ifndef _SIGNAL_CPOLE_H_
#define _SIGNAL_CPOLE_H_

#include "HvHeavyInternal.h"
#include "HvSignalDel1.h"

#ifdef __cplusplus
extern "C" {
#endif

// implements y[n] = x[n] - a*y[n-1]
// H(z) = 1/(1+a*z^-1)
typedef struct SignalCPole {
#if HV_SIMD_AVX
  SignalDel1 sDel1_8kZ3w;
  SignalDel1 sDel1_sy3YC;
  SignalDel1 sDel1_GjjjE;
  SignalDel1 sDel1_52HYk;
  SignalDel1 sDel1_lXpu3;
  SignalDel1 sDel1_orza7;
  SignalDel1 sDel1_K7tpr;
  SignalDel1 sDel1_yfNee;
  SignalDel1 sDel1_hl63z;
  SignalDel1 sDel1_etJkN;
  SignalDel1 sDel1_BW4zg;
  SignalDel1 sDel1_0z8gy;
  SignalDel1 sDel1_0F5sm;
  SignalDel1 sDel1_i4rAW;
  SignalDel1 sDel1_ux1Jv;
  SignalDel1 sDel1_FVaak;
  SignalDel1 sDel1_oEc0p;
  SignalDel1 sDel1_1AVVz;
  SignalDel1 sDel1_qp6ty;
  SignalDel1 sDel1_bkttO;
  SignalDel1 sDel1_60VsH;
  SignalDel1 sDel1_TbY4f;
  SignalDel1 sDel1_bNHHm;
  SignalDel1 sDel1_mijYH;
  SignalDel1 sDel1_anxSw;
  SignalDel1 sDel1_YiP2h;
  SignalDel1 sDel1_anyeH;
  SignalDel1 sDel1_Vtq0Y;
  hv_bufferf_t ymr;
  hv_bufferf_t ymi;
#elif HV_SIMD_SSE || HV_SIMD_NEON
  SignalDel1 sDel1_j0EQa;
  SignalDel1 sDel1_4REN6;
  SignalDel1 sDel1_5z88r;
  SignalDel1 sDel1_CxDdp;
  SignalDel1 sDel1_8zCWF;
  SignalDel1 sDel1_1A4op;
  SignalDel1 sDel1_ldSdM;
  SignalDel1 sDel1_sOZ64;
  SignalDel1 sDel1_mpbqn;
  SignalDel1 sDel1_sBC7F;
  SignalDel1 sDel1_bZG8k;
  SignalDel1 sDel1_Wtjof;
  hv_bufferf_t ymr;
  hv_bufferf_t ymi;
#else
  hv_bufferf_t ymr;
  hv_bufferf_t ymi;
#endif
} SignalCPole;

hv_size_t sCPole_init(SignalCPole *o);

void sCPole_onMessage(HeavyContextInterface *_c, SignalCPole *o, int letIn, const HvMessage *m);

#if _WIN32 && !_WIN64
#define __hv_cpole_f(o, bIn0, bIn1, bIn2, bIn3, bOut0, bOut1) __hv_cpole_f_win32(o, &bIn0, &bIn1, &bIn2, &bIn3, bOut0, bOut1)
static inline void __hv_cpole_f_win32(SignalCPole *o,
	hv_bInf_t *_bIn0, hv_bInf_t *_bIn1, hv_bInf_t *_bIn2, hv_bInf_t *_bIn3,
	hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  hv_bInf_t bIn0 = *_bIn0;
  hv_bInf_t bIn1 = *_bIn1;
  hv_bInf_t bIn2 = *_bIn2;
  hv_bInf_t bIn3 = *_bIn3;
#else
static inline void __hv_cpole_f(SignalCPole *o,
    hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bInf_t bIn2, hv_bInf_t bIn3,
    hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
#endif
#if HV_SIMD_AVX
  hv_bufferf_t Bf0, Bf1, Bf2, Bf3, Bf4, Bf5, Bf6, Bf7, Bf8, Bf9, Bf10, Bf11, Bf12, Bf13, Bf14;
  __hv_del1_f(&o->sDel1_8kZ3w, bIn0, VOf(Bf0));
  __hv_del1_f(&o->sDel1_sy3YC, bIn1, VOf(Bf1));
  __hv_mul_f(VIf(Bf1), bIn2, VOf(Bf2));
  __hv_fma_f(VIf(Bf0), bIn3, VIf(Bf2), VOf(Bf2));
  __hv_mul_f(VIf(Bf0), bIn2, VOf(Bf3));
  __hv_mul_f(VIf(Bf1), bIn3, VOf(Bf4));
  __hv_sub_f(VIf(Bf3), VIf(Bf4), VOf(Bf4));
  __hv_sub_f(bIn1, VIf(Bf2), VOf(Bf2));
  __hv_del1_f(&o->sDel1_GjjjE, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_52HYk, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_lXpu3, bIn2, VOf(Bf3));
  __hv_del1_f(&o->sDel1_orza7, bIn3, VOf(Bf5));
  __hv_mul_f(bIn2, VIf(Bf3), VOf(Bf6));
  __hv_mul_f(bIn3, VIf(Bf5), VOf(Bf7));
  __hv_sub_f(VIf(Bf6), VIf(Bf7), VOf(Bf7));
  __hv_mul_f(bIn3, VIf(Bf3), VOf(Bf6));
  __hv_fma_f(bIn2, VIf(Bf5), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(VIf(Bf0), VIf(Bf6), VOf(Bf8));
  __hv_fma_f(VIf(Bf1), VIf(Bf7), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf0), VIf(Bf7), VOf(Bf9));
  __hv_mul_f(VIf(Bf1), VIf(Bf6), VOf(Bf10));
  __hv_sub_f(VIf(Bf9), VIf(Bf10), VOf(Bf10));
  __hv_add_f(VIf(Bf2), VIf(Bf8), VOf(Bf8));
  __hv_del1_f(&o->sDel1_K7tpr, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_yfNee, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_hl63z, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_etJkN, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf7), VIf(Bf3), VOf(Bf2));
  __hv_mul_f(VIf(Bf6), VIf(Bf5), VOf(Bf9));
  __hv_sub_f(VIf(Bf2), VIf(Bf9), VOf(Bf9));
  __hv_mul_f(VIf(Bf7), VIf(Bf5), VOf(Bf7));
  __hv_fma_f(VIf(Bf6), VIf(Bf3), VIf(Bf7), VOf(Bf7));
  __hv_mul_f(VIf(Bf1), VIf(Bf9), VOf(Bf6));
  __hv_fma_f(VIf(Bf0), VIf(Bf7), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(VIf(Bf0), VIf(Bf9), VOf(Bf2));
  __hv_mul_f(VIf(Bf1), VIf(Bf7), VOf(Bf11));
  __hv_sub_f(VIf(Bf2), VIf(Bf11), VOf(Bf11));
  __hv_sub_f(VIf(Bf8), VIf(Bf6), VOf(Bf6));
  __hv_del1_f(&o->sDel1_BW4zg, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_0z8gy, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_0F5sm, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_i4rAW, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf7), VIf(Bf3), VOf(Bf8));
  __hv_fma_f(VIf(Bf9), VIf(Bf5), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf9), VIf(Bf3), VOf(Bf9));
  __hv_mul_f(VIf(Bf7), VIf(Bf5), VOf(Bf7));
  __hv_sub_f(VIf(Bf9), VIf(Bf7), VOf(Bf7));
  __hv_mul_f(VIf(Bf0), VIf(Bf7), VOf(Bf9));
  __hv_mul_f(VIf(Bf1), VIf(Bf8), VOf(Bf2));
  __hv_sub_f(VIf(Bf9), VIf(Bf2), VOf(Bf2));
  __hv_mul_f(VIf(Bf0), VIf(Bf8), VOf(Bf9));
  __hv_fma_f(VIf(Bf1), VIf(Bf7), VIf(Bf9), VOf(Bf9));
  __hv_add_f(VIf(Bf6), VIf(Bf9), VOf(Bf9));
  __hv_del1_f(&o->sDel1_ux1Jv, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_FVaak, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_oEc0p, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_1AVVz, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf8), VIf(Bf3), VOf(Bf6));
  __hv_fma_f(VIf(Bf7), VIf(Bf5), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(VIf(Bf7), VIf(Bf3), VOf(Bf7));
  __hv_mul_f(VIf(Bf8), VIf(Bf5), VOf(Bf8));
  __hv_sub_f(VIf(Bf7), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf0), VIf(Bf8), VOf(Bf7));
  __hv_mul_f(VIf(Bf1), VIf(Bf6), VOf(Bf12));
  __hv_sub_f(VIf(Bf7), VIf(Bf12), VOf(Bf12));
  __hv_mul_f(VIf(Bf1), VIf(Bf8), VOf(Bf7));
  __hv_fma_f(VIf(Bf0), VIf(Bf6), VIf(Bf7), VOf(Bf7));
  __hv_sub_f(VIf(Bf9), VIf(Bf7), VOf(Bf7));
  __hv_del1_f(&o->sDel1_qp6ty, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_bkttO, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_60VsH, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_TbY4f, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf6), VIf(Bf3), VOf(Bf9));
  __hv_fma_f(VIf(Bf8), VIf(Bf5), VIf(Bf9), VOf(Bf9));
  __hv_mul_f(VIf(Bf8), VIf(Bf3), VOf(Bf8));
  __hv_mul_f(VIf(Bf6), VIf(Bf5), VOf(Bf6));
  __hv_sub_f(VIf(Bf8), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(VIf(Bf0), VIf(Bf9), VOf(Bf8));
  __hv_fma_f(VIf(Bf1), VIf(Bf6), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf0), VIf(Bf6), VOf(Bf13));
  __hv_mul_f(VIf(Bf1), VIf(Bf9), VOf(Bf14));
  __hv_sub_f(VIf(Bf13), VIf(Bf14), VOf(Bf14));
  __hv_add_f(VIf(Bf7), VIf(Bf8), VOf(Bf8));
  __hv_del1_f(&o->sDel1_bNHHm, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_mijYH, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_anxSw, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_YiP2h, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf6), VIf(Bf5), VOf(Bf7));
  __hv_fma_f(VIf(Bf9), VIf(Bf3), VIf(Bf7), VOf(Bf7));
  __hv_mul_f(VIf(Bf6), VIf(Bf3), VOf(Bf6));
  __hv_mul_f(VIf(Bf9), VIf(Bf5), VOf(Bf9));
  __hv_sub_f(VIf(Bf6), VIf(Bf9), VOf(Bf9));
  __hv_mul_f(VIf(Bf0), VIf(Bf9), VOf(Bf6));
  __hv_mul_f(VIf(Bf1), VIf(Bf7), VOf(Bf13));
  __hv_sub_f(VIf(Bf6), VIf(Bf13), VOf(Bf13));
  __hv_mul_f(VIf(Bf0), VIf(Bf7), VOf(Bf0));
  __hv_fma_f(VIf(Bf1), VIf(Bf9), VIf(Bf0), VOf(Bf0));
  __hv_sub_f(VIf(Bf8), VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_anyeH, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_Vtq0Y, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf9), VIf(Bf3), VOf(Bf8));
  __hv_mul_f(VIf(Bf7), VIf(Bf5), VOf(Bf1));
  __hv_sub_f(VIf(Bf8), VIf(Bf1), VOf(Bf1));
  __hv_mul_f(VIf(Bf9), VIf(Bf5), VOf(Bf5));
  __hv_fma_f(VIf(Bf7), VIf(Bf3), VIf(Bf5), VOf(Bf5));
  Bf3 = o->ymr;
  Bf4 = o->ymi;
  __hv_mul_f(VIf(Bf1), VIf(Bf3), VOf(Bf9));
  __hv_mul_f(VIf(Bf5), VIf(Bf7), VOf(Bf8));
  __hv_sub_f(VIf(Bf9), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf1), VIf(Bf7), VOf(Bf7));
  __hv_fma_f(VIf(Bf5), VIf(Bf3), VIf(Bf7), VOf(Bf7));
  __hv_add_f(VIf(Bf0), VIf(Bf7), VOf(Bf7));
  o->ymi = Bf7;
  __hv_sub_f(bIn0, VIf(Bf4), VOf(Bf4));
  __hv_add_f(VIf(Bf4), VIf(Bf10), VOf(Bf10));
  __hv_sub_f(VIf(Bf10), VIf(Bf11), VOf(Bf11));
  __hv_add_f(VIf(Bf11), VIf(Bf2), VOf(Bf2));
  __hv_sub_f(VIf(Bf2), VIf(Bf12), VOf(Bf12));
  __hv_add_f(VIf(Bf12), VIf(Bf14), VOf(Bf14));
  __hv_sub_f(VIf(Bf14), VIf(Bf13), VOf(Bf13));
  __hv_add_f(VIf(Bf13), VIf(Bf8), VOf(Bf8));
  *bOut0 = Bf8;
  *bOut0 = Bf7;
  o->ymr = Bf8;
#elif HV_SIMD_SSE || HV_SIMD_NEON
  hv_bufferf_t Bf0, Bf1, Bf2, Bf3, Bf4, Bf5, Bf6, Bf7, Bf8, Bf9, Bf10;
  __hv_del1_f(&o->sDel1_j0EQa, bIn0, VOf(Bf0));
  __hv_del1_f(&o->sDel1_4REN6, bIn1, VOf(Bf1));
  __hv_mul_f(VIf(Bf0), bIn3, VOf(Bf2));
  __hv_fma_f(VIf(Bf1), bIn2, VIf(Bf2), VOf(Bf2));
  __hv_mul_f(VIf(Bf0), bIn2, VOf(Bf3));
  __hv_mul_f(VIf(Bf1), bIn3, VOf(Bf4));
  __hv_sub_f(VIf(Bf3), VIf(Bf4), VOf(Bf4));
  __hv_sub_f(bIn1, VIf(Bf2), VOf(Bf2));
  __hv_del1_f(&o->sDel1_5z88r, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_CxDdp, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_8zCWF, bIn2, VOf(Bf3));
  __hv_del1_f(&o->sDel1_1A4op, bIn3, VOf(Bf5));
  __hv_mul_f(bIn3, VIf(Bf3), VOf(Bf6));
  __hv_fma_f(bIn2, VIf(Bf5), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(bIn2, VIf(Bf3), VOf(Bf7));
  __hv_mul_f(bIn3, VIf(Bf5), VOf(Bf8));
  __hv_sub_f(VIf(Bf7), VIf(Bf8), VOf(Bf8));
  __hv_mul_f(VIf(Bf0), VIf(Bf8), VOf(Bf7));
  __hv_mul_f(VIf(Bf1), VIf(Bf6), VOf(Bf9));
  __hv_sub_f(VIf(Bf7), VIf(Bf9), VOf(Bf9));
  __hv_mul_f(VIf(Bf0), VIf(Bf6), VOf(Bf7));
  __hv_fma_f(VIf(Bf1), VIf(Bf8), VIf(Bf7), VOf(Bf7));
  __hv_add_f(VIf(Bf2), VIf(Bf7), VOf(Bf7));
  __hv_del1_f(&o->sDel1_ldSdM, VIf(Bf0), VOf(Bf0));
  __hv_del1_f(&o->sDel1_sOZ64, VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_mpbqn, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_sBC7F, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf6), VIf(Bf3), VOf(Bf2));
  __hv_fma_f(VIf(Bf8), VIf(Bf5), VIf(Bf2), VOf(Bf2));
  __hv_mul_f(VIf(Bf8), VIf(Bf3), VOf(Bf8));
  __hv_mul_f(VIf(Bf6), VIf(Bf5), VOf(Bf6));
  __hv_sub_f(VIf(Bf8), VIf(Bf6), VOf(Bf6));
  __hv_mul_f(VIf(Bf0), VIf(Bf6), VOf(Bf8));
  __hv_mul_f(VIf(Bf1), VIf(Bf2), VOf(Bf10));
  __hv_sub_f(VIf(Bf8), VIf(Bf10), VOf(Bf10));
  __hv_mul_f(VIf(Bf1), VIf(Bf6), VOf(Bf1));
  __hv_fma_f(VIf(Bf0), VIf(Bf2), VIf(Bf1), VOf(Bf1));
  __hv_sub_f(VIf(Bf7), VIf(Bf1), VOf(Bf1));
  __hv_del1_f(&o->sDel1_bZG8k, VIf(Bf3), VOf(Bf3));
  __hv_del1_f(&o->sDel1_Wtjof, VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf6), VIf(Bf3), VOf(Bf7));
  __hv_mul_f(VIf(Bf2), VIf(Bf5), VOf(Bf0));
  __hv_sub_f(VIf(Bf7), VIf(Bf0), VOf(Bf0));
  __hv_mul_f(VIf(Bf2), VIf(Bf3), VOf(Bf3));
  __hv_fma_f(VIf(Bf6), VIf(Bf5), VIf(Bf3), VOf(Bf3));
  Bf5 = o->ymr;
  Bf6 = o->ymi;
  __hv_mul_f(VIf(Bf3), VIf(Bf5), VOf(Bf2));
  __hv_fma_f(VIf(Bf0), VIf(Bf6), VIf(Bf2), VOf(Bf2));
  __hv_mul_f(VIf(Bf0), VIf(Bf5), VOf(Bf5));
  __hv_mul_f(VIf(Bf3), VIf(Bf6), VOf(Bf6));
  __hv_sub_f(VIf(Bf5), VIf(Bf6), VOf(Bf6));
  __hv_add_f(VIf(Bf1), VIf(Bf2), VOf(Bf2));
  *bOut1 = Bf2;
  __hv_sub_f(bIn0, VIf(Bf4), VOf(Bf4));
  __hv_add_f(VIf(Bf4), VIf(Bf9), VOf(Bf9));
  __hv_sub_f(VIf(Bf9), VIf(Bf10), VOf(Bf10));
  __hv_add_f(VIf(Bf10), VIf(Bf6), VOf(Bf6));
  *bOut0 = Bf6;
  o->ymr = Bf6;
  o->ymi = Bf2;
#else
  *bOut0 = bIn0 - (bIn2*o->ymr - bIn3*o->ymi);
  *bOut1 = bIn1 - (bIn2*o->ymi + bIn3*o->ymr);
  o->ymr = *bOut0;
  o->ymi = *bOut1;
#endif
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_CPOLE_H_
