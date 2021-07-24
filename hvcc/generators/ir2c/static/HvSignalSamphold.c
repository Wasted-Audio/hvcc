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

#include "HvSignalSamphold.h"

hv_size_t sSamphold_init(SignalSamphold *o) {
#if HV_SIMD_AVX
  o->s = _mm256_setzero_ps();
#elif HV_SIMD_SSE
  o->s = _mm_setzero_ps();
#elif HV_SIMD_NEON
  o->s = vdupq_n_f32(0.0f);
#else
  o->s = 0.0f;
#endif
  return 0;
}

void sSamphold_onMessage(HeavyContextInterface *_c, SignalSamphold *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    case 2: {
      if (msg_isFloat(m,0)) {
#if HV_SIMD_AVX
        o->s = _mm256_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_SSE
        o->s = _mm_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_NEON
        o->s = vdupq_n_f32(msg_getFloat(m,0));
#else
        o->s = msg_getFloat(m,0);
#endif
      }
      break;
    }
    default: break;
  }
}
