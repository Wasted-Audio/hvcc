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

#include "HvSignalTabread.h"

hv_size_t sTabread_init(SignalTabread *o, HvTable *table, bool forceAlignedLoads) {
  o->table = table;
  o->head = 0;
  o->forceAlignedLoads = forceAlignedLoads;
  return 0;
}

void sTabread_onMessage(HeavyContextInterface *_c, SignalTabread *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      if (o->table != NULL) {
        switch (msg_getType(m,0)) {
          case HV_MSG_BANG: o->head = 0; break;
          case HV_MSG_FLOAT: {
            hv_uint32_t h = (hv_uint32_t) hv_abs_f(msg_getFloat(m,0));
            if (msg_getFloat(m,0) < 0.0f) {
              // if input is negative, wrap around the end of the table
              h = hTable_getSize(o->table) - h;
            }
            o->head = o->forceAlignedLoads ? (h & ~HV_N_SIMD_MASK) : h;

            // output new head
            HvMessage *n = HV_MESSAGE_ON_STACK(1);
            msg_initWithFloat(n, msg_getTimestamp(m), (float) o->head);
            sendMessage(_c, 1, n);
            break;
          }
          default: break;
        }
      }
      break;
    }
    case 1: {
      if (msg_isHashLike(m,0)) {
        o->table = hv_table_get(_c, msg_getHash(m,0));
      }
      break;
    }
    default: break;
  }
}



#if HV_APPLE
#pragma mark - Tabhead
#endif

void sTabhead_onMessage(HeavyContextInterface *_c, SignalTabhead *o, const HvMessage *m) {
  if (msg_isHashLike(m,0)) {
    o->table = hv_table_get(_c, msg_getHash(m,0));
  }
}

hv_size_t sTabhead_init(SignalTabhead *o, HvTable *table) {
  o->table = table;
  return 0;
}
