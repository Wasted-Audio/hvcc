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

#include "HvControlUnop.h"

void cUnop_onMessage(HeavyContextInterface *_c, UnopType op, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  if (msg_isFloat(m, 0)) {
    float f = msg_getFloat(m, 0);
    switch (op) {
      case HV_UNOP_SIN: f = hv_sin_f(f); break;
      case HV_UNOP_SINH: f = hv_sinh_f(f); break;
      case HV_UNOP_COS: f = hv_cos_f(f); break;
      case HV_UNOP_COSH: f = hv_cosh_f(f); break;
      case HV_UNOP_TAN: f = hv_tan_f(f); break;
      case HV_UNOP_TANH: f = hv_tanh_f(f); break;
      case HV_UNOP_ASIN: f = hv_asin_f(f); break;
      case HV_UNOP_ASINH: f = hv_asinh_f(f); break;
      case HV_UNOP_ACOS: f = hv_acos_f(f); break;
      case HV_UNOP_ACOSH: f = hv_acosh_f(f); break;
      case HV_UNOP_ATAN: f = hv_atan_f(f); break;
      case HV_UNOP_ATANH: f = hv_atanh_f(f); break;
      case HV_UNOP_EXP: f = hv_exp_f(f); break;
      case HV_UNOP_ABS: f = hv_abs_f(f); break;
      case HV_UNOP_SQRT: f = (f > 0.0f) ? hv_sqrt_f(f) : 0.0f; break;
      case HV_UNOP_LOG: f = (f > 0.0f) ? hv_log_f(f) : 0.0f; break;
      case HV_UNOP_LOG2: f = (f > 0.0f) ? (1.442695040888963f*hv_log_f(f)) : 0.0f; break;
      case HV_UNOP_LOG10: f = (f > 0.0f) ? (0.434294481903252f*hv_log_f(f)) : 0.0f; break;
      case HV_UNOP_CEIL: f = hv_ceil_f(f); break;
      case HV_UNOP_FLOOR: f = hv_floor_f(f); break;
      case HV_UNOP_ROUND: f = hv_round_f(f); break;
      default: return;
    }
    HvMessage *n = HV_MESSAGE_ON_STACK(1);
    msg_initWithFloat(n, m->timestamp, f);
    sendMessage(_c, 0, n);
  }
}
