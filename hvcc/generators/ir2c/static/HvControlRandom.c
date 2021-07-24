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

#include "HvControlRandom.h"

// http://www.firstpr.com.au/dsp/rand31
// http://en.wikipedia.org/wiki/Lehmer_random_number_generator

hv_size_t cRandom_init(ControlRandom *o, int seed) {
  o->state = (seed != 0) ? seed : 1;
  return 0;
}

void cRandom_onMessage(HeavyContextInterface *_c, ControlRandom *o, int inletIndex, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (inletIndex) {
    case 0: {
      HvMessage *n = HV_MESSAGE_ON_STACK(1);
      o->state = (hv_uint32_t) ((((unsigned long long) o->state) * 279470273UL) % 4294967291UL);
      float f = ((float) (o->state >> 9)) * 0.00000011920929f;
      msg_initWithFloat(n, msg_getTimestamp(m), f);
      sendMessage(_c, 0, n);
      break;
    }
    case 1: {
      if (msg_isFloat(m,0)) {
        o->state = (hv_uint32_t) msg_getFloat(m,0);
      }
      break;
    }
    default: break;
  }
}
