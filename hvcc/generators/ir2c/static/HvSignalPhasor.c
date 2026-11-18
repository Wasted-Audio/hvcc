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

#include "HvSignalPhasor.h"

#define HV_PHASOR_2_32 4294967296.0

  static void sPhasor_updatePhase(SignalPhasor *o, hv_uint32_t p) {
    o->phase = p;
}

// input phase is in the range of [0,1]. It is independent of o->phase.
static void sPhasor_k_updatePhase(SignalPhasor *o, hv_uint32_t p) {
  o->phase = p;
}

static void sPhasor_k_updateFrequency(SignalPhasor *o, float f, double r) {
  o->step.s = (hv_int32_t) (f*(HV_PHASOR_2_32/r));
  o->inc = o->step.s;
  // no need to update phase
}

hv_size_t sPhasor_init(SignalPhasor *o, double samplerate) {
  o->phase = 0;
  o->inc = 0;
  o->step.f2sc = (float) (HV_PHASOR_2_32/samplerate);
  return 0;
}

void sPhasor_onMessage(HeavyContextInterface *_c, SignalPhasor *o, int letIn, const HvMessage *m) {
  if (letIn == 1) {
    if (msg_isFloat(m,0)) {
      float p = msg_getFloat(m,0);
      while (p < 0.0f) p += 1.0f; // wrap phase to [0,1]
      while (p > 1.0f) p -= 1.0f;
      sPhasor_updatePhase(o, (hv_uint32_t) (p * HV_PHASOR_2_32));
    }
  }
}

hv_size_t sPhasor_k_init(SignalPhasor *o, float frequency, double samplerate) {
  __hv_zero_i((hv_bOuti_t) &o->phase);
  sPhasor_k_updateFrequency(o, frequency, samplerate);
  return 0;
}

void sPhasor_k_onMessage(HeavyContextInterface *_c, SignalPhasor *o, int letIn, const HvMessage *m) {
  if (msg_isFloat(m,0)) {
    switch (letIn) {
      case 0: sPhasor_k_updateFrequency(o, msg_getFloat(m,0), hv_getSampleRate(_c)); break;
      case 1: {
        float p = msg_getFloat(m,0);
        while (p < 0.0f) p += 1.0f; // wrap phase to [0,1]
        while (p > 1.0f) p -= 1.0f;
        sPhasor_k_updatePhase(o, (hv_uint32_t) (p * HV_PHASOR_2_32));
        break;
      }
      default: break;
    }
  }
}
