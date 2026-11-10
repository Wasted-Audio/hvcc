/**
 * Copyright (c) 2026 Wasted Audio
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

#ifndef _SIGNAL_SCHMITT_H_
#define _SIGNAL_SCHMITT_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalSchmitt {
  float tVal;
  float tDeb;
  float rVal;
  float rDeb;
  float state;
  int debounceCounter;
  hv_uint32_t processedSamples;
  hv_uint32_t lastBlockStart;
} SignalSchmitt;

hv_size_t sSchmitt_init(SignalSchmitt *o, float tVal, float tDeb, float rVal, float rDeb);

static inline void __hv_schmitt_f(HeavyContextInterface *_c, SignalSchmitt *o, hv_bInf_t bIn,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  float bIn_array[HV_N_SIMD];
  __hv_store_f(bIn_array, bIn);

  hv_uint32_t blockStart = hv_getCurrentSample(_c);
  if (o->lastBlockStart != blockStart) {
    o->lastBlockStart = blockStart;
    o->processedSamples = 0;
  }

  for (int i = 0; i < HV_N_SIMD; i++) {
    float val = bIn_array[i];
    hv_uint32_t currentSample = blockStart + o->processedSamples;

    if (o->debounceCounter > 0) {
      o->debounceCounter--;
    }

    if (o->state != 0.0f) {
      if (val < o->rVal && o->debounceCounter == 0) {
        o->state = 0.0f;
        HvMessage *const m = HV_MESSAGE_ON_STACK(1);
        msg_initWithBang(m, currentSample);
        hv_scheduleMessageForObject(_c, m, sendMessage, 1);
        o->debounceCounter = (int) (o->rDeb * hv_getSampleRate(_c) / 1000.0f);
      }
    } else {
      if (val >= o->tVal && o->debounceCounter == 0) {
        o->state = 1.0f;
        HvMessage *const m = HV_MESSAGE_ON_STACK(1);
        msg_initWithBang(m, currentSample);
        hv_scheduleMessageForObject(_c, m, sendMessage, 0);
        o->debounceCounter = (int) (o->tDeb * hv_getSampleRate(_c) / 1000.0f);
      }
    }
    o->processedSamples++;
  }
}

void sSchmitt_onMessage(HeavyContextInterface *_c, SignalSchmitt *o, int letIndex,
    const HvMessage *m);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_SCHMITT_H_
