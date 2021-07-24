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

#include "HvSignalTabwrite.h"

hv_size_t sTabwrite_init(SignalTabwrite *o, HvTable *table) {
  o->table = table;
  o->head = 0;
  return 0;
}

void sTabwrite_onMessage(HeavyContextInterface *_c, SignalTabwrite *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    // inlet 0 is the signal inlet
    case 1: {
      switch (msg_getType(m,0)) {
        case HV_MSG_BANG: o->head = 0; break;
        case HV_MSG_FLOAT: {
          o->head = (msg_getFloat(m,0) >= 0.0f) ? (hv_uint32_t) msg_getFloat(m,0) : HV_TABWRITE_STOPPED;
          break;
        }
        case HV_MSG_SYMBOL: {
          if (msg_compareSymbol(m, 0, "stop")) {
            o->head = HV_TABWRITE_STOPPED;
          }
          break;
        }
        default: break;
      }
      break;
    }
    case 2: {
      if (msg_isHashLike(m,0)) {
        o->table = hv_table_get(_c, msg_getHash(m,0));
      }
      break;
    }
    default: break;
  }
}
