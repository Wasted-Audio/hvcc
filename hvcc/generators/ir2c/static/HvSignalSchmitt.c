/**
 * Copyright (c) 2026 Wasted Audio
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

#include "HvSignalSchmitt.h"

hv_size_t sSchmitt_init(SignalSchmitt *o, float tVal, float tDeb, float rVal, float rDeb) {
  o->tVal = tVal;
  o->tDeb = tDeb;
  o->rVal = rVal;
  o->rDeb = rDeb;
  o->state = 0;
  return 0;
}

void sSchmitt_onMessage(HeavyContextInterface *_c, SignalSchmitt *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    case 2: {
      if (msg_isFloat(m,0)) {
        o->tVal = msg_getFloat(m,0);
      }
      break;
    }
    case 3: {
      if (msg_isFloat(m,0)) {
        o->state = (int) msg_getFloat(m,0);
      }
      break;
    }
    default: break;
  }
}
