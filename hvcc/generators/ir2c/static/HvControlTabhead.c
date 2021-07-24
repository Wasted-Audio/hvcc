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

#include "HvControlTabhead.h"

hv_size_t cTabhead_init(ControlTabhead *o, HvTable *table) {
  o->table = table;
  return 0;
}

void cTabhead_onMessage(HeavyContextInterface *_c, ControlTabhead *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      if (msg_getType(m,0) == HV_MSG_BANG) {
        // get current head of table
        HvMessage *n = HV_MESSAGE_ON_STACK(1);
        msg_initWithFloat(n, msg_getTimestamp(m), (float) hTable_getHead(o->table));
        sendMessage(_c, 0, n);
      }
      break;
    }
    case 1: {
      if (msg_isHashLike(m,0)) {
        // set a new table
        o->table = hv_table_get(_c, msg_getHash(m,0));
      }
      break;
    }
    default: break;
  }
}
