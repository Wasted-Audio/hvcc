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

#include "HvSignalRPole.h"

hv_size_t sRPole_init(SignalRPole *o) {
#if HV_SIMD_AVX
  sDel1_init(&o->sDel1_fxiLN);
  sDel1_init(&o->sDel1_kjkpV);
  sDel1_init(&o->sDel1_dkIWc);
  sDel1_init(&o->sDel1_bVeoW);
  sDel1_init(&o->sDel1_PulZn);
  sDel1_init(&o->sDel1_yTFig);
  sDel1_init(&o->sDel1_Is9Qf);
  sDel1_init(&o->sDel1_LIyNt);
  sDel1_init(&o->sDel1_VqpU3);
  sDel1_init(&o->sDel1_ZVYeg);
  sDel1_init(&o->sDel1_IVAZh);
  sDel1_init(&o->sDel1_F8WrY);
  sDel1_init(&o->sDel1_rkFMy);
  sDel1_init(&o->sDel1_BeqSK);
  __hv_zero_f(&o->ym);
#elif HV_SIMD_SSE || HV_SIMD_NEON
  sDel1_init(&o->sDel1_i8Twk);
  sDel1_init(&o->sDel1_KYibU);
  sDel1_init(&o->sDel1_spa5V);
  sDel1_init(&o->sDel1_3HXdb);
  sDel1_init(&o->sDel1_Aj1oK);
  sDel1_init(&o->sDel1_jNX1g);
  __hv_zero_f(&o->ym);
#else
  o->ym = 0.0f;
#endif
  return 0;
}

void sRPole_onMessage(HeavyContextInterface *_c, SignalRPole *o, int letIn, const HvMessage *m) {
  // TODO
}
