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

#include "HvControlPack.h"

hv_size_t cPack_init(ControlPack *o, int nargs, ...) {
  hv_size_t numBytes = msg_getCoreSize(nargs);
  o->msg = (HvMessage *) hv_malloc(numBytes);
  hv_assert(o->msg != NULL);
  msg_init(o->msg, nargs, 0);

  // variable arguments are used as float initialisers for the pack elements
  va_list ap;
  va_start(ap, nargs);
  for (int i = 0; i < nargs; ++i) {
    msg_setFloat(o->msg, i, (float) va_arg(ap, double));
  }
  va_end(ap);
  return numBytes;
}

void cPack_free(ControlPack *o) {
  hv_free(o->msg);
}

void cPack_onMessage(HeavyContextInterface *_c, ControlPack *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  // ensure let index is less than number elements in internal msg
  int numElements = msg_getNumElements(o->msg);
  switch (letIn) {
    case 0: { // first inlet stores all values of input msg and triggers an output
      for (int i = hv_min_i(numElements, msg_getNumElements(m))-1; i >= 0; --i) {
        switch (msg_getType(m, i)) {
          case HV_MSG_FLOAT: msg_setFloat(o->msg, i, msg_getFloat(m, i)); break;
          case HV_MSG_SYMBOL:
          case HV_MSG_HASH: msg_setHash(o->msg, i, msg_getHash(m, i)); break;
          default: break;
        }
      }
      msg_setTimestamp(o->msg, msg_getTimestamp(m));
      sendMessage(_c, 0, o->msg);
      break;
    }
    default: { // rest of inlets just store values
      switch (msg_getType(m, 0)) {
        case HV_MSG_FLOAT: msg_setFloat(o->msg, letIn, msg_getFloat(m, 0)); break;
        case HV_MSG_SYMBOL:
        case HV_MSG_HASH: msg_setHash(o->msg, letIn, msg_getHash(m, 0)); break;
        default: break;
      }
      break;
    }
  }
}
