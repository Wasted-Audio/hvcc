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

#include "HvSignalCPole.h"

hv_size_t sCPole_init(SignalCPole *o) {
#if HV_SIMD_AVX
  sDel1_init(&o->sDel1_8kZ3w);
  sDel1_init(&o->sDel1_sy3YC);
  sDel1_init(&o->sDel1_GjjjE);
  sDel1_init(&o->sDel1_52HYk);
  sDel1_init(&o->sDel1_lXpu3);
  sDel1_init(&o->sDel1_orza7);
  sDel1_init(&o->sDel1_K7tpr);
  sDel1_init(&o->sDel1_yfNee);
  sDel1_init(&o->sDel1_hl63z);
  sDel1_init(&o->sDel1_etJkN);
  sDel1_init(&o->sDel1_BW4zg);
  sDel1_init(&o->sDel1_0z8gy);
  sDel1_init(&o->sDel1_0F5sm);
  sDel1_init(&o->sDel1_i4rAW);
  sDel1_init(&o->sDel1_ux1Jv);
  sDel1_init(&o->sDel1_FVaak);
  sDel1_init(&o->sDel1_oEc0p);
  sDel1_init(&o->sDel1_1AVVz);
  sDel1_init(&o->sDel1_qp6ty);
  sDel1_init(&o->sDel1_bkttO);
  sDel1_init(&o->sDel1_60VsH);
  sDel1_init(&o->sDel1_TbY4f);
  sDel1_init(&o->sDel1_bNHHm);
  sDel1_init(&o->sDel1_mijYH);
  sDel1_init(&o->sDel1_anxSw);
  sDel1_init(&o->sDel1_YiP2h);
  sDel1_init(&o->sDel1_anyeH);
  sDel1_init(&o->sDel1_Vtq0Y);
  __hv_zero_f(&o->ymr);
  __hv_zero_f(&o->ymi);
#elif HV_SIMD_SSE || HV_SIMD_NEON
  sDel1_init(&o->sDel1_j0EQa);
  sDel1_init(&o->sDel1_4REN6);
  sDel1_init(&o->sDel1_5z88r);
  sDel1_init(&o->sDel1_CxDdp);
  sDel1_init(&o->sDel1_8zCWF);
  sDel1_init(&o->sDel1_1A4op);
  sDel1_init(&o->sDel1_ldSdM);
  sDel1_init(&o->sDel1_sOZ64);
  sDel1_init(&o->sDel1_mpbqn);
  sDel1_init(&o->sDel1_sBC7F);
  sDel1_init(&o->sDel1_bZG8k);
  sDel1_init(&o->sDel1_Wtjof);
  __hv_zero_f(&o->ymr);
  __hv_zero_f(&o->ymi);
#else
  o->ymr = 0.0f;
  o->ymi = 0.0f;
#endif
  return 0;
}

void sCPole_onMessage(HeavyContextInterface *_c, SignalCPole *o, int letIn, const HvMessage *m) {
  // TODO
}
