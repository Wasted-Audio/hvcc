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
  if (bIn1 != 0.0f) o->s = bIn0;
  *bOut = o->s;
}

void sSamphold_onMessage(HeavyContextInterface *_c, SignalSamphold *o, int letIndex,
    const HvMessage *m, void *sendMessage);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_SAMPHOLD_H_
