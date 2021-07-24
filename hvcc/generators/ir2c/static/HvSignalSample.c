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

#include "HvSignalSample.h"

#define __HV_SAMPLE_NULL -1

hv_size_t sSample_init(SignalSample *o) {
  o->i = __HV_SAMPLE_NULL;
  return 0;
}

void sSample_onMessage(HeavyContextInterface *_c, SignalSample *o, int letIndex, const HvMessage *m) {
  o->i = msg_getTimestamp(m);
}

void __hv_sample_f(HeavyContextInterface *_c, SignalSample *o, hv_bInf_t bIn,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  if (o->i != __HV_SAMPLE_NULL) {

#if HV_SIMD_AVX || HV_SIMD_SSE
    const float *const b = (float *) &bIn;
    float out = b[o->i & HV_N_SIMD_MASK];
#elif HV_SIMD_NEON
    float out = bIn[o->i & HV_N_SIMD_MASK];
#else // HV_SIMD_NONE
    float out = bIn;
#endif

    HvMessage *n = HV_MESSAGE_ON_STACK(1);
    hv_uint32_t ts = (o->i + HV_N_SIMD) & ~HV_N_SIMD_MASK; // start of next block
    msg_initWithFloat(n, ts, out);
    hv_scheduleMessageForObject(_c, n, sendMessage, 0);
    o->i = __HV_SAMPLE_NULL; // reset the index
  }
}
