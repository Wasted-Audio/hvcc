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

#ifndef _SIGNAL_LINE_H_
#define _SIGNAL_LINE_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalLine {
  hv_bufferi_t n; // remaining samples to target
  hv_bufferf_t x; // current output
  hv_bufferf_t m; // increment
  hv_bufferf_t t; // target value
} SignalLine;

hv_size_t sLine_init(SignalLine *o);

static inline void __hv_line_f(SignalLine *o, hv_bOutf_t bOut) {
  *bOut = (o->n < 0) ? o->t : o->x;
  o->n -= HV_N_SIMD;
  o->x += o->m;
}

void sLine_onMessage(HeavyContextInterface *_c, SignalLine *o, int letIndex,
    const HvMessage *m, void *sendMessage);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_LINE_H_
