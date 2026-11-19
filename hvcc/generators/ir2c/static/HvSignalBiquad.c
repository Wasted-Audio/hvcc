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

#include "HvSignalBiquad.h"

// http://reanimator-web.appspot.com/articles/simdiir
// https://webaudio.github.io/Audio-EQ-Cookbook/audio-eq-cookbook.html

hv_size_t sBiquad_init(SignalBiquad *o) {
  o->xm1 = 0.0f;
  o->xm2 = 0.0f;
  o->ym1 = 0.0f;
  o->ym2 = 0.0f;
  return 0;
}

#if _WIN32 && !_WIN64
void __hv_biquad_f_win32(SignalBiquad *o, hv_bInf_t *_bIn, hv_bInf_t *_bX0, hv_bInf_t *_bX1, hv_bInf_t *_bX2, hv_bInf_t *_bY1, hv_bInf_t *_bY2, hv_bOutf_t bOut) {
  hv_bInf_t bIn = *_bIn;
  hv_bInf_t bX0 = *_bX0;
  hv_bInf_t bX1 = *_bX1;
  hv_bInf_t bX2 = *_bX2;
  hv_bInf_t bY1 = *_bY1;
  hv_bInf_t bY2 = *_bY2;
#else
void __hv_biquad_f(SignalBiquad *o, hv_bInf_t bIn, hv_bInf_t bX0, hv_bInf_t bX1, hv_bInf_t bX2, hv_bInf_t bY1, hv_bInf_t bY2, hv_bOutf_t bOut) {
#endif
  const float y = bIn*bX0 + o->xm1*bX1 + o->xm2*bX2 - o->ym1*bY1 - o->ym2*bY2;
  o->xm2 = o->xm1; o->xm1 = bIn;
  o->ym2 = o->ym1; o->ym1 = y;
  *bOut = y;
}

static void sBiquad_k_updateCoefficients(SignalBiquad_k *const o) {
#if DEBUG
  // inspect the filter coefficients to ensure that the filter is stable
  // 1/((1-a*z^-1) * (1-b*z^-1))
  float k = (o->a1*o->a1) - (4.0f*o->a2);
  float l = hv_sqrt_f(hv_abs_f(k));

  float m_alpha = 0.0f;
  float m_beta = 0.0f;
  if (k < 0.0f) {
    // alpha is complex
    float r_alpha = o->a1 * 0.5f;
    float i_alpha = l * 0.5f;
    m_alpha = (r_alpha*r_alpha + i_alpha*i_alpha); // |alpha|^2

    float r_beta = (o->a2 * r_alpha) / m_alpha;
    float i_beta = (o->a2 * -i_alpha) / m_alpha;
    m_alpha = hv_sqrt_f(m_alpha);
    m_beta = hv_sqrt_f(r_beta*r_beta + i_beta*i_beta);
  } else {
    // alpha is real
    float alpha = (o->a1 + l) * 0.5f;
    float beta = o->a2 / alpha;
    m_alpha = hv_abs_f(alpha);
    m_beta = hv_abs_f(beta);
  }

  hv_assert(m_alpha < 1.0f);
  hv_assert(m_beta < 1.0f);
#endif
}

hv_size_t sBiquad_k_init(SignalBiquad_k *o, float b0, float b1, float b2, float a1, float a2) {
  // initialise filter coefficients
  o->b0 = b0;
  o->b1 = b1;
  o->b2 = b2;
  o->a1 = a1;
  o->a2 = a2;
  sBiquad_k_updateCoefficients(o);

  // clear filter state
  o->xm1 = 0.0f;
  o->xm2 = 0.0f;
  o->ym1 = 0.0f;
  o->ym2 = 0.0f;
  return 0;
}

void sBiquad_k_onMessage(SignalBiquad_k *o, int letIn, const HvMessage *m) {
  if (msg_isFloat(m,0)) {
    switch (letIn) {
      case 1: o->b0 = msg_getFloat(m,0); break;
      case 2: o->b1 = msg_getFloat(m,0); break;
      case 3: o->b2 = msg_getFloat(m,0); break;
      case 4: o->a1 = msg_getFloat(m,0); break;
      case 5: o->a2 = msg_getFloat(m,0); break;
      default: return;
    }
    sBiquad_k_updateCoefficients(o);
  }
}
