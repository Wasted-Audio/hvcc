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

#include "HvSignalDel1.h"

hv_size_t sDel1_init(SignalDel1 *o) {
#if HV_SIMD_AVX
  o->x = _mm256_setzero_ps();
#elif HV_SIMD_SSE
  o->x = _mm_setzero_ps();
#elif HV_SIMD_NEON
  o->x = vdupq_n_f32(0.0f);
#else
  o->x = 0.0f;
#endif
  return 0;
}

void sDel1_onMessage(HeavyContextInterface *_c, SignalDel1 *o, int letIn, const HvMessage *m) {
  if (letIn == 2) {
    if (msg_compareSymbol(m, 0, "clear")) {
#if HV_SIMD_AVX
      o->x = _mm256_setzero_ps();
#elif HV_SIMD_SSE
      o->x = _mm_setzero_ps();
#elif HV_SIMD_NEON
      o->x = vdupq_n_f32(0.0f);
#else
      o->x = 0.0f;
#endif
    }
  }
}
