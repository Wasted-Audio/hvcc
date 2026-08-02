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
  o->tDeb = hv_max_f(0.0f, tDeb);
  o->rVal = rVal;
  o->rDeb = hv_max_f(0.0f, rDeb);
  o->state = 0.0f;
  o->debounceCounter = 0;
  o->processedSamples = 0;
  o->lastBlockStart = 0xFFFFFFFF;
  return 0;
}

void sSchmitt_onMessage(HeavyContextInterface *_c, SignalSchmitt *o, int letIndex,
    const HvMessage *m) {
  switch (letIndex) {
    case 1: {
      if (msg_getNumElements(m) >= 4) {
        o->tVal = msg_getFloat(m, 0);
        o->tDeb = hv_max_f(0.0f, msg_getFloat(m, 1));
        o->rVal = msg_getFloat(m, 2);
        o->rDeb = hv_max_f(0.0f, msg_getFloat(m, 3));
      }
      break;
    }
    case 2: {
      if (msg_isFloat(m, 0)) {
        o->state = (msg_getFloat(m, 0) != 0.0f) ? 1.0f : 0.0f;
        o->debounceCounter = 0;
      }
      break;
    }
    default: break;
  }
}
