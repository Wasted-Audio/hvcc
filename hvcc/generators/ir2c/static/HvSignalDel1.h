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

#ifndef _SIGNAL_DEL1_H_
#define _SIGNAL_DEL1_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalDel1 {
  hv_bufferf_t x;
} SignalDel1;

hv_size_t sDel1_init(SignalDel1 *o);

void sDel1_onMessage(HeavyContextInterface *_c, SignalDel1 *o, int letIn, const HvMessage *m);

static inline void __hv_del1_f(SignalDel1 *o, hv_bInf_t bIn0, hv_bOutf_t bOut) {
  *bOut = o->x;
  o->x = bIn0;
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_DEL1_H_
