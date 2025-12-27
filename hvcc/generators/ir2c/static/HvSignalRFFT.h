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

#ifdef __cplusplus
extern "C" {
#endif


typedef struct SignalRFFT {
  struct HvTable input;
  struct HvTable outputReal;
  struct HvTable outputImagin;
} SignalRFFT;

hv_size_t sRFFT_init(SignalRFFT *o, const int size);
void sRFFT_free(SignalRFFT *o);
void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex, const HvMessage *m, void *sendMessage);
void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1);

typedef struct SignalRIFFT {
  struct HvTable inputReal;
  struct HvTable inputImagin;
  struct HvTable output;
} SignalRIFFT;

hv_size_t sRIFFT_init(SignalRIFFT *o, const int size);
void sRIFFT_free(SignalRIFFT *o);
void sRIFFT_onMessage(HeavyContextInterface *_c, SignalRIFFT *o, int letIndex, const HvMessage *m, void *sendMessage);
void __hv_rifft_f(SignalRIFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_RFFT_H_
