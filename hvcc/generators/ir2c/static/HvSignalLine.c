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

#include "HvSignalLine.h"

hv_size_t sLine_init(SignalLine *o) {
  o->n = 0;
  o->x = 0.0f;
  o->m = 0.0f;
  o->t = 0.0f;
  return 0;
}

void sLine_onMessage(HeavyContextInterface *_c, SignalLine *o, int letIn,
  const HvMessage *m, void *sendMessage) {
  if (msg_isFloat(m,0)) {
    if (msg_isFloat(m,1)) {
      // new ramp
      int n = (int) hv_millisecondsToSamples(_c, msg_getFloat(m,1));
      o->x = (o->n > 0) ? (o->x + o->m) : o->t; // new current value
      o->n = n; // new distance to target
      o->m = (msg_getFloat(m,0) - o->x) / ((float) n); // slope per sample
      o->t = msg_getFloat(m,0);
    } else {
      // Jump to value
      o->n = 0;
      o->x = msg_getFloat(m,0);
      o->m = 0.0f;
      o->t = msg_getFloat(m,0);
    }
  } else if (msg_compareSymbol(m,0,"stop")) {
    // Stop line at current position
    float x = (o->n > 0) ? (o->x + o->m) : o->t;
    o->n = 0;
    o->x = x;
    o->m = 0.0f;
    o->t = x;
  }
}
