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

#include "HvControlDelay.h"

hv_size_t cDelay_init(HeavyContextInterface *_c, ControlDelay *o, float delayMs) {
  o->delay = hv_millisecondsToSamples(_c, delayMs);
  hv_memclear(o->msgs, __HV_DELAY_MAX_MESSAGES*sizeof(HvMessage *));
  return 0;
}

void cDelay_onMessage(HeavyContextInterface *_c, ControlDelay *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      if (msg_compareSymbol(m, 0, "flush")) {
        // send all messages immediately
        for (int i = 0; i < __HV_DELAY_MAX_MESSAGES; i++) {
          HvMessage *n = o->msgs[i];
          if (n != NULL) {
            msg_setTimestamp(n, msg_getTimestamp(m)); // update the timestamp to now
            sendMessage(_c, 0, n); // send the message
            hv_cancelMessage(_c, n, sendMessage); // then clear it
            // NOTE(mhroth): there may be a problem here if a flushed message causes a clear message to return
            // to this object in the same step
          }
        }
        hv_memclear(o->msgs, __HV_DELAY_MAX_MESSAGES*sizeof(HvMessage *));
      } else if (msg_compareSymbol(m, 0, "clear")) {
        // cancel (clear) all (pending) messages
        for (int i = 0; i < __HV_DELAY_MAX_MESSAGES; i++) {
          HvMessage *n = o->msgs[i];
          if (n != NULL) {
            hv_cancelMessage(_c, n, sendMessage);
          }
        }
        hv_memclear(o->msgs, __HV_DELAY_MAX_MESSAGES*sizeof(HvMessage *));
      } else {
        hv_uint32_t ts = msg_getTimestamp(m);
        msg_setTimestamp((HvMessage *) m, ts+o->delay); // update the timestamp to set the delay
        int i;
        for (i = 0; i < __HV_DELAY_MAX_MESSAGES; i++) {
          if (o->msgs[i] == NULL) {
            o->msgs[i] = hv_scheduleMessageForObject(_c, m, sendMessage, 0);
            break;
          }
        }
        hv_assert((i < __HV_DELAY_MAX_MESSAGES) && // scheduled message limit reached
            "[__delay] cannot track any more messages. Try increasing the size of __HV_DELAY_MAX_MESSAGES.");
        msg_setTimestamp((HvMessage *) m, ts); // return to the original timestamp
      }
      break;
    }
    case 1: {
      if (msg_isFloat(m,0)) {
        // set delay in milliseconds (cannot be negative!)
        o->delay = hv_millisecondsToSamples(_c, msg_getFloat(m,0));
      }
      break;
    }
    case 2: {
      if (msg_isFloat(m,0)) {
        // set delay in samples (cannot be negative!)
        o->delay = (hv_uint32_t) hv_max_f(0.0f, msg_getFloat(m,0));
      }
      break;
    }
    default: break;
  }
}

void cDelay_clearExecutingMessage(ControlDelay *o, const HvMessage *m) {
  for (int i = 0; i < __HV_DELAY_MAX_MESSAGES; ++i) {
    if (o->msgs[i] == m) {
      o->msgs[i] = NULL;
      break;
    }
  }
}
