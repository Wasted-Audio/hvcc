/**
 * Copyright (c) 2022-2025 Daniel Billotte, Wasted Audio
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

hv_size_t cExpr_init(ControlExpr *o, float(*eval_fptr)(const float*)) {
  o->eval_fptr = eval_fptr;
  for(int i=0; i < MAX_EXPR_ARGS; i++) {
    o->args[i] = 0.0f;
  }
  return 0;
}

void cExpr_free(ControlExpr *o) {
  ;
}

void cExpr_onMessage(HeavyContextInterface *_c, ControlExpr *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {

  int numElements = msg_getNumElements(m);
  switch (letIn) {
    case 0: { // first inlet stores all values of input msg and triggers an output
      if (msg_isBang(m,0)) {
        ; // pass through to sending the msg below
      } else {
        for (int i = hv_min_i(numElements, msg_getNumElements(m))-1; i >= 0; --i) {
          if (msg_isFloat(m, i)) {
            o->args[i] = msg_getFloat(m, i);
          }
        }
      }

      // send result of expression
      HvMessage *n = HV_MESSAGE_ON_STACK(1);
      float f = o->eval_fptr(o->args);
      msg_initWithFloat(n, msg_getTimestamp(m), f);
      sendMessage(_c, 0, n);
      break;
    }
    default: { // rest of inlets just store values
      if (msg_isFloat(m,0)) {
        o->args[letIn] = msg_getFloat(m, 0);
      }
      break;
    }
  }
}
