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
  HvTable *table; // the table to read
  hv_uint32_t head;
  hv_uint32_t end;
  int blocksize;
} SignalTabreceive;

// random access to a table
hv_size_t sTabreceive_init(SignalTabreceive *o, HvTable *table, int blocksize);


static inline void __hv_tabreceive_f(SignalTabreceive *o, hv_bIni_t bIn, hv_bOutf_t bOut) {
  const float *const b = hTable_getBuffer(o->table);
#if HV_SIMD_AVX

#elif HV_SIMD_SSE

#elif HV_SIMD_NEON

#else // HV_SIMD_NONE

#endif
}


void sTabreceive_onMessage(HeavyContextInterface *_c, SignalTabreceive *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));


#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABRECEIVE_H_
