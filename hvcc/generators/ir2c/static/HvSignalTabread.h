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

#ifndef _HEAVY_SIGNAL_TABREAD_H_
#define _HEAVY_SIGNAL_TABREAD_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalTabread {
  HvTable *table; // the table to read
  hv_uint32_t head;
  hv_uint32_t end;
  bool forceAlignedLoads; // false by default, true if using __hv_tabread_f
  bool playing; // false by default, only __hv_tabread_stoppable_f may respond to it
} SignalTabread;

// random access to a table
hv_size_t sTabread_init(SignalTabread *o, HvTable *table, bool forceAlignedLoads);



#if HV_APPLE
#pragma mark - Tabread - Random Access
#endif

static inline void __hv_tabread_if(SignalTabread *o, hv_bIni_t bIn, hv_bOutf_t bOut) {
  const float *const b = hTable_getBuffer(o->table);
  hv_assert(bIn >= 0 && ((hv_uint32_t) bIn < hTable_getAllocated(o->table)));

  *bOut = b[bIn];
}



#if HV_APPLE
#pragma mark - Tabread - Linear Access
#endif

// this tabread never stops reading. It is mainly intended for linear reads that loop around a table.
static inline void __hv_tabread_f(SignalTabread *o, hv_bOutf_t bOut) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getAllocated(o->table)); // assert that we always read within the table bounds
  hv_uint32_t head = o->head;
  *bOut = *(hTable_getBuffer(o->table) + head);
  o->head = head + HV_N_SIMD;
}

// unaligned linear tabread, as above
static inline void __hv_tabreadu_f(SignalTabread *o, hv_bOutf_t bOut) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getAllocated(o->table)); // assert that we always read within the table bounds
  hv_uint32_t head = o->head;
  *bOut = *(hTable_getBuffer(o->table) + head);
  o->head = head + HV_N_SIMD;
}

// this tabread can be instructed to stop. It is mainly intended for linear reads that only process a portion of a buffer.
static inline void __hv_tabread_stoppable_f(HeavyContextInterface *_c, SignalTabread *o, hv_bOutf_t bOut,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *))
{
  hv_uint32_t head = o->head;
  if (head >= hTable_getAllocated(o->table)) { // stop when we reach the table bounds
    o->playing = false;
  }
  if (!o->playing) {
    __hv_zero_f(bOut); // output silence when not playing
  } else {
    if (o->end > o->head) { // only play when end is further than play head
      *bOut = *(hTable_getBuffer(o->table) + head);
      o->head = head + HV_N_SIMD;
    } else {
      o->playing = false;
      __hv_zero_f(bOut); // output silence when not playing
      HvMessage *n = HV_MESSAGE_ON_STACK(1);
      msg_initWithBang(n, 0);
      sendMessage(_c, 2, n);
    }
  }
}

void sTabread_onMessage(HeavyContextInterface *_c, SignalTabread *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));



#if HV_APPLE
#pragma mark - Tabhead
#endif

typedef struct SignalTabhead {
  HvTable *table;
} SignalTabhead;

hv_size_t sTabhead_init(SignalTabhead *o, HvTable *table);

static inline void __hv_tabhead_f(SignalTabhead *o, hv_bOutf_t bOut) {
  *bOut = (float) hTable_getHead(o->table);
}

void sTabhead_onMessage(HeavyContextInterface *_c, SignalTabhead *o, const HvMessage *m);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABREAD_H_
