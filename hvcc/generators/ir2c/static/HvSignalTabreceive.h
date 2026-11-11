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

#ifndef _HEAVY_SIGNAL_TABRECEIVE_H_
#define _HEAVY_SIGNAL_TABRECEIVE_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalTabreceive {
  HvTable *table;
  hv_uint32_t head;
  int blocksize;
} SignalTabreceive;

hv_size_t sTabreceive_init(SignalTabreceive *o, HvTable *table, int blocksize);


static inline void __hv_tabreceive_f(SignalTabreceive *o, hv_bOutf_t bOut) {
  const hv_uint32_t length = (o->table != NULL) ? hTable_getLength(o->table) : 0;
  hv_uint32_t head = o->head;

  if (head >= length) {
    // beyond the table: rest of the block is silence
    __hv_zero_f(bOut);
  } else if (head + HV_N_SIMD <= length) {
    // fully inside the table
    __hv_load_f(hTable_getBuffer(o->table) + head, bOut);
  } else {
    // partial vector: copy valid samples, zero the remaining lanes
    const hv_uint32_t n = length - head;
    const float *const b = hTable_getBuffer(o->table) + head;
    float tail[HV_N_SIMD];
    for (hv_uint32_t i = 0; i < HV_N_SIMD; ++i) tail[i] = (i < n) ? b[i] : 0.0f;
    __hv_load_f(tail, bOut);
  }

  // window is [0, blocksize); wrap at the end of it
  const hv_uint32_t bs = (o->blocksize > 0) ? (hv_uint32_t) o->blocksize : HV_N_SIMD;
  head += HV_N_SIMD;
  o->head = (head < bs) ? head : 0;
}


void sTabreceive_onMessage(HeavyContextInterface *_c, SignalTabreceive *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));


#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABRECEIVE_H_
