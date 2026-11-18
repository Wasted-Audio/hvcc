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

#ifndef _HEAVY_SIGNAL_TABWRITE_H_
#define _HEAVY_SIGNAL_TABWRITE_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HV_TABWRITE_STOPPED (~(hv_uint32_t)0x0)

typedef struct SignalTabwrite {
  HvTable *table;
  hv_uint32_t head; // local write head. Where this object has most recently written to the table.
} SignalTabwrite;

hv_size_t sTabwrite_init(SignalTabwrite *o, HvTable *table);

void sTabwrite_onMessage(HeavyContextInterface *_c, SignalTabwrite *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));

// linear write to table
static inline void __hv_tabwrite_f(SignalTabwrite *o, hv_bInf_t bIn) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getSize(o->table)); // assert that the table bounds are respected
  hv_uint32_t head = o->head;
  *(hTable_getBuffer(o->table) + head) = bIn;
  head += HV_N_SIMD;
  o->head = head; // update local write head
  hTable_setHead(o->table, head); // update the remote write head (e.g. for use by vd~)
}

// linear unaligned write to table
static inline void __hv_tabwriteu_f(SignalTabwrite *o, hv_bInf_t bIn) {
  hv_uint32_t head = o->head;
  *(hTable_getBuffer(o->table) + head) = bIn;
  head += HV_N_SIMD;
  o->head = head; // update local write head
  hTable_setHead(o->table, head); // update remote write head
}

// this tabwrite can be instructed to stop. It is mainly intended for linear reads that only process a portion of a buffer.
// Stores are unaligned, which can be slow but allows any indicies to be written to.
// TODO(mhroth): this is not stopping!
static inline void __hv_tabwrite_stoppable_f(SignalTabwrite *o, hv_bInf_t bIn) {
  if (o->head != HV_TABWRITE_STOPPED) {
    *(hTable_getBuffer(o->table) + o->head) = bIn;
    o->head += HV_N_SIMD;
  }
}

// random write to table
static inline void __hv_tabwrite_if(SignalTabwrite *o, hv_bIni_t bIn0, hv_bInf_t bIn1) {
  float *const b = hTable_getBuffer(o->table);
  b[bIn0] = bIn1;
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABWRITE_H_
