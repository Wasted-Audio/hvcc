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

#include "HvControlBinop.h"

hv_size_t cBinop_init(ControlBinop *o, float k) {
  o->k = k;
  return 0;
}

static float cBinop_perform_op(BinopType op, float f, float k) {
  switch (op) {
    case HV_BINOP_ADD: return f + k;
    case HV_BINOP_SUBTRACT: return f - k;
    case HV_BINOP_MULTIPLY: return f * k;
    case HV_BINOP_DIVIDE: return (k != 0.0f) ? (f/k) : 0.0f;
    case HV_BINOP_INT_DIV: {
      const int ik = (int) k;
      return (ik != 0) ? (float) (((int) f) / ik) : 0.0f;
    }
    case HV_BINOP_MOD_BIPOLAR: {
      const int ik = (int) k;
      return (ik != 0) ? (float) (((int) f) % ik) : 0.0f;
    }
    case HV_BINOP_MOD_UNIPOLAR: {
      f = (k == 0.0f) ? 0.0f : (float) ((int) f % (int) k);
      return (f < 0.0f) ? f + hv_abs_f(k) : f;
    }
    case HV_BINOP_BIT_LEFTSHIFT: return (float) (((int) f) << ((int) k));
    case HV_BINOP_BIT_RIGHTSHIFT: return (float) (((int) f) >> ((int) k));
    case HV_BINOP_BIT_AND: return (float) ((int) f & (int) k);
    case HV_BINOP_BIT_XOR: return (float) ((int) f ^ (int) k);
    case HV_BINOP_BIT_OR: return (float) ((int) f | (int) k);
    case HV_BINOP_EQ: return (f == k) ? 1.0f : 0.0f;
    case HV_BINOP_NEQ: return (f != k) ? 1.0f : 0.0f;
    case HV_BINOP_LOGICAL_AND: return ((f == 0.0f) || (k == 0.0f)) ? 0.0f : 1.0f;
    case HV_BINOP_LOGICAL_OR: return ((f == 0.0f) && (k == 0.0f)) ? 0.0f : 1.0f;
    case HV_BINOP_LESS_THAN: return (f < k) ? 1.0f : 0.0f;
    case HV_BINOP_LESS_THAN_EQL: return (f <= k) ? 1.0f : 0.0f;
    case HV_BINOP_GREATER_THAN: return (f > k) ? 1.0f : 0.0f;
    case HV_BINOP_GREATER_THAN_EQL: return (f >= k) ? 1.0f : 0.0f;
    case HV_BINOP_MAX: return hv_max_f(f, k);
    case HV_BINOP_MIN: return hv_min_f(f, k);
    case HV_BINOP_POW: return (f > 0.0f) ? hv_pow_f(f, k) : 0.0f;
    case HV_BINOP_ATAN2: return ((f == 0.0f) && (k == 0.0f)) ? 0.0f : hv_atan2_f(f, k);
    default: return 0.0f;
  }
}

void cBinop_onMessage(HeavyContextInterface *_c, ControlBinop *o, BinopType op, int letIn,
    const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      if (msg_isFloat(m, 0)) {
        // Note(joe): supporting Pd's ability to perform operations of packs
        // of floats is likely to not be supported in the future.
        if (msg_isFloat(m, 1)) o->k = msg_getFloat(m, 1);
        HvMessage *n = HV_MESSAGE_ON_STACK(1);
        float f = cBinop_perform_op(op, msg_getFloat(m, 0), o->k);
        msg_initWithFloat(n, msg_getTimestamp(m), f);
        sendMessage(_c, 0, n);
      }
      break;
    }
    case 1: {
      if (msg_isFloat(m, 0)) {
        o->k = msg_getFloat(m, 0);
      }
      break;
    }
    default: break;
  }
}

void cBinop_k_onMessage(HeavyContextInterface *_c, void *o, BinopType op, float k,
    int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  if (msg_isFloat(m, 0)) {
    // NOTE(mhroth): Heavy does not support sending bangs to binop objects to return the previous output
    float f = (msg_isFloat(m, 1)) ? msg_getFloat(m, 1) : k;
    HvMessage *n = HV_MESSAGE_ON_STACK(1);
    f = cBinop_perform_op(op, msg_getFloat(m, 0), f);
    msg_initWithFloat(n, msg_getTimestamp(m), f);
    sendMessage(_c, 0, n);
  }
}
