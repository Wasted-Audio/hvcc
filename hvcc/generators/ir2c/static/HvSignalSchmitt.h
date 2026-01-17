/**
 * Copyright (c) 2026 Wasted Audio
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

#ifndef _SIGNAL_SCHMITT_H_
#define _SIGNAL_SCHMITT_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalSchmitt {
  hv_bufferf_t tVal;
  hv_bufferf_t tDeb;
  hv_bufferf_t rVal;
  hv_bufferf_t rDeb;
  hv_bufferi_t state;
} SignalSchmitt;

hv_size_t sSchmitt_init(SignalSchmitt *o, hv_bufferf_t tVal, hv_bufferf_t tDeb, hv_bufferf_t rVal, hv_bufferf_t rDeb);

static inline void __hv_schmitt_f(HeavyContextInterface *_c, SignalSchmitt *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
    // do schmitt triggering
}

void sSchmitt_onMessage(HeavyContextInterface *_c, SignalSchmitt *o, int letIndex,
    const HvMessage *m, void *sendMessage);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_SCHMITT_H_
