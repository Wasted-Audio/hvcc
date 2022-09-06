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

#include "HvControlExpr.h"

// hv_size_t cExpr_init(ControlExpr *o, int nargs, ...) {
//   hv_size_t numBytes = msg_getCoreSize(nargs);
//   o->msg = (HvMessage *) hv_malloc(numBytes);
//   hv_assert(o->msg != NULL);
//   msg_init(o->msg, nargs, 0);

//   // variable arguments are used as float initialisers for the Expr elements
//   va_list ap;
//   va_start(ap, nargs);
//   for (int i = 0; i < nargs; ++i) {
//     msg_setFloat(o->msg, i, (float) va_arg(ap, double));
//   }
//   va_end(ap);
//   return numBytes;
// }

// void cExpr_free(ControlExpr *o) {
//   hv_free(o->msg);
// }

void cExpr_onMessage(HeavyContextInterface *_c, ControlExpr *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  // ensure let index is less than number elements in internal msg
  // int numElements = msg_getNumElements(o->msg);
  switch (letIn) {
    case 0: { // first inlet stores all values of input msg and triggers an output
      break;
    }
    default: { // rest of inlets just store values
      break;
    }
  }
}
