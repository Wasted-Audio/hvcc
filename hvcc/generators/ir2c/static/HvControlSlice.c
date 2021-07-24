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

#include "HvControlSlice.h"

hv_size_t cSlice_init(ControlSlice *o, int i, int n) {
  o->i = i;
  o->n = n;
  return 0;
}

void cSlice_onMessage(HeavyContextInterface *_c, ControlSlice *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      // if the start point is greater than the number of elements in the source message, do nothing
      if (o->i < msg_getNumElements(m)) {
        int x = msg_getNumElements(m) - o->i; // number of elements in the new message
        if (o->n > 0) x = hv_min_i(x, o->n);
        HvMessage *n = HV_MESSAGE_ON_STACK(x);
        msg_init(n, x, msg_getTimestamp(m));
        hv_memcpy(&n->elem, &m->elem+o->i, x*sizeof(Element));
        sendMessage(_c, 0, n);
      } else {
        // if nothing can be sliced, send a bang out of the right outlet
        HvMessage *n = HV_MESSAGE_ON_STACK(1);
        msg_initWithBang(n, msg_getTimestamp(m));
        sendMessage(_c, 1, n);
      }
      break;
    }
    case 1: {
      if (msg_isFloat(m,0)) {
        o->i = (int) msg_getFloat(m,0);
        if (msg_isFloat(m,1)) {
          o->n = (int) msg_getFloat(m,1);
        }
      }
      break;
    }
    case 2: {
      if (msg_isFloat(m,0)) {
        o->n = (int) msg_getFloat(m,0);
      }
      break;
    }
    default: break;
  }
}
