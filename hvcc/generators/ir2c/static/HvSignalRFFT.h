/**
 * Copyright (c) 2023 Wasted Audio
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

#ifndef _SIGNAL_RFFT_H_
#define _SIGNAL_RFFT_H_

#include "HvHeavyInternal.h"
#include "pffft.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifdef HV_SIMD_NONE
#define PFFFT_SIMD_DISABLE
#endif

typedef struct SignalRFFT {
  struct HvTable *table;
  struct HvTable inputs;
  struct PFFFT_Setup *setup;
} SignalRFFT;

hv_size_t sRFFT_init(SignalRFFT *o, struct HvTable *table, const int size);

void sRFFT_free(SignalRFFT *o);

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage);

void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1);

void __hv_rifft_f(SignalRFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_RFFT_H_
