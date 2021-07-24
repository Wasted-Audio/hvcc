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

#include "HvSignalLine.h"

hv_size_t sLine_init(SignalLine *o) {
#if HV_SIMD_AVX
  o->n = _mm_setzero_si128();
  o->x = _mm256_setzero_ps();
  o->m = _mm256_setzero_ps();
  o->t = _mm256_setzero_ps();
#elif HV_SIMD_SSE
  o->n = _mm_setzero_si128();
  o->x = _mm_setzero_ps();
  o->m = _mm_setzero_ps();
  o->t = _mm_setzero_ps();
#elif HV_SIMD_NEON
  o->n = vdupq_n_s32(0);
  o->x = vdupq_n_f32(0.0f);
  o->m = vdupq_n_f32(0.0f);
  o->t = vdupq_n_f32(0.0f);
#else // HV_SIMD_NONE
  o->n = 0;
  o->x = 0.0f;
  o->m = 0.0f;
  o->t = 0.0f;
#endif
  return 0;
}

void sLine_onMessage(HeavyContextInterface *_c, SignalLine *o, int letIn,
  const HvMessage *m, void *sendMessage) {
  if (msg_isFloat(m,0)) {
    if (msg_isFloat(m,1)) {
      // new ramp
      int n = (int) hv_millisecondsToSamples(_c, msg_getFloat(m,1));
#if HV_SIMD_AVX
      float x = (o->n[1] > 0) ? (o->x[7] + (o->m[7]/8.0f)) : o->t[7]; // current output value
      float s = (msg_getFloat(m,0) - x) / ((float) n); // slope per sample
      o->n = _mm_set_epi32(n-3, n-2, n-1, n);
      o->x = _mm256_set_ps(x+7.0f*s, x+6.0f*s, x+5.0f*s, x+4.0f*s, x+3.0f*s, x+2.0f*s, x+s, x);
      o->m = _mm256_set1_ps(8.0f*s);
      o->t = _mm256_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_SSE
      const hv_int32_t *const on = (hv_int32_t *) &o->n;
      const float *const ox = (float *) &o->x;
      const float *const om = (float *) &o->m;
      const float *const ot = (float *) &o->t;

      float x = (on[3] > 0) ? (ox[3] + (om[3]/4.0f)) : ot[3];
      float s = (msg_getFloat(m,0) - x) / ((float) n); // slope per sample
      o->n = _mm_set_epi32(n-3, n-2, n-1, n);
      o->x = _mm_set_ps(x+3.0f*s, x+2.0f*s, x+s, x);
      o->m = _mm_set1_ps(4.0f*s);
      o->t = _mm_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_NEON
      float x = (o->n[3] > 0) ? (o->x[3] + (o->m[3]/4.0f)) : o->t[3];
      float s = (msg_getFloat(m,0) - x) / ((float) n);
      o->n = (int32x4_t) {n, n-1, n-2, n-3};
      o->x = (float32x4_t) {x, x+s, x+2.0f*s, x+3.0f*s};
      o->m = vdupq_n_f32(4.0f*s);
      o->t = vdupq_n_f32(msg_getFloat(m,0));
#else // HV_SIMD_NONE
      o->x = (o->n > 0) ? (o->x + o->m) : o->t; // new current value
      o->n = n; // new distance to target
      o->m = (msg_getFloat(m,0) - o->x) / ((float) n); // slope per sample
      o->t = msg_getFloat(m,0);
#endif
    } else {
      // Jump to value
#if HV_SIMD_AVX
      o->n = _mm_setzero_si128();
      o->x = _mm256_set1_ps(msg_getFloat(m,0));
      o->m = _mm256_setzero_ps();
      o->t = _mm256_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_SSE
      o->n = _mm_setzero_si128();
      o->x = _mm_set1_ps(msg_getFloat(m,0));
      o->m = _mm_setzero_ps();
      o->t = _mm_set1_ps(msg_getFloat(m,0));
#elif HV_SIMD_NEON
      o->n = vdupq_n_s32(0);
      o->x = vdupq_n_f32(msg_getFloat(m,0));
      o->m = vdupq_n_f32(0.0f);
      o->t = vdupq_n_f32(msg_getFloat(m,0));
#else // HV_SIMD_NONE
      o->n = 0;
      o->x = msg_getFloat(m,0);
      o->m = 0.0f;
      o->t = msg_getFloat(m,0);
#endif
    }
  } else if (msg_compareSymbol(m,0,"stop")) {
    // Stop line at current position
#if HV_SIMD_AVX
    // note o->n[1] is a 64-bit integer; two packed 32-bit ints. We only want to know if the high int is positive,
    // which can be done simply by testing the long int for positiveness.
    float x = (o->n[1] > 0) ? (o->x[7] + (o->m[7]/8.0f)) : o->t[7];
    o->n = _mm_setzero_si128();
    o->x = _mm256_set1_ps(x);
    o->m = _mm256_setzero_ps();
    o->t = _mm256_set1_ps(x);
#elif HV_SIMD_SSE
    const hv_int32_t *const on = (hv_int32_t *) &o->n;
    const float *const ox = (float *) &o->x;
    const float *const om = (float *) &o->m;
    const float *const ot = (float *) &o->t;
    float x = (on[3] > 0) ? (ox[3] + (om[3]/4.0f)) : ot[3];
    o->n = _mm_setzero_si128();
    o->x = _mm_set1_ps(x);
    o->m = _mm_setzero_ps();
    o->t = _mm_set1_ps(x);
#elif HV_SIMD_NEON
    float x = (o->n[3] > 0) ? (o->x[3] + (o->m[3]/4.0f)) : o->t[3];
    o->n = vdupq_n_s32(0);
    o->x = vdupq_n_f32(x);
    o->m = vdupq_n_f32(0.0f);
    o->t = vdupq_n_f32(x);
#else // HV_SIMD_NONE
    o->n = 0;
    o->x += o->m;
    o->m = 0.0f;
    o->t = o->x;
#endif
  }
}
