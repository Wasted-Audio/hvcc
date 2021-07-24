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

#include "HvControlVar.h"

hv_size_t cVar_init_f(ControlVar *o, float k) {
  o->e.type = HV_MSG_FLOAT;
  o->e.data.f = k;
  return 0;
}

hv_size_t cVar_init_s(ControlVar *o, const char *s) {
  o->e.type = HV_MSG_HASH;
  o->e.data.h = hv_string_to_hash(s);
  return 0;
}

void cVar_free(ControlVar *o) {
  // nothing to do
}

void cVar_onMessage(HeavyContextInterface *_c, ControlVar *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      switch (msg_getType(m,0)) {
        case HV_MSG_BANG: {
          HvMessage *n = HV_MESSAGE_ON_STACK(1);
          if (o->e.type == HV_MSG_FLOAT) msg_initWithFloat(n, msg_getTimestamp(m), o->e.data.f);
          else if (o->e.type == HV_MSG_HASH) msg_initWithHash(n, msg_getTimestamp(m), o->e.data.h);
          else return;
          sendMessage(_c, 0, n);
          break;
        }
        case HV_MSG_FLOAT: {
          o->e.type = HV_MSG_FLOAT;
          o->e.data.f = msg_getFloat(m,0);
          sendMessage(_c, 0, m);
          break;
        }
        case HV_MSG_SYMBOL:
        case HV_MSG_HASH: {
          o->e.type = HV_MSG_HASH;
          o->e.data.h = msg_getHash(m,0);
          sendMessage(_c, 0, m);
          break;
        }
        default: return;
      }
      break;
    }
    case 1: {
      switch (msg_getType(m,0)) {
        case HV_MSG_FLOAT: {
          o->e.type = HV_MSG_FLOAT;
          o->e.data.f = msg_getFloat(m,0);
          break;
        }
        case HV_MSG_SYMBOL:
        case HV_MSG_HASH: {
          o->e.type = HV_MSG_HASH;
          o->e.data.h = msg_getHash(m,0);
          break;
        }
        default: break;
      }
    }
    default: return;
  }
}
