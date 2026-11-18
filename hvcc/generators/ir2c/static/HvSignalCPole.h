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
  *bOut0 = bIn0 - (bIn2*o->ymr - bIn3*o->ymi);
  *bOut1 = bIn1 - (bIn2*o->ymi + bIn3*o->ymr);
  o->ymr = *bOut0;
  o->ymi = *bOut1;
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_CPOLE_H_
