/**
 * Copyright (c) 2023 Wasted Audio
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

#include "HvSignalRFFT.h"
#include "HvMath.h"

#include <stddef.h>
#include <stdlib.h>

#include "kissfft/kiss_fft.h"
#include "kissfft/kiss_fftr.h"

// Heavy is strictly float. Fail at compile time rather than silently
// transforming at the wrong precision.
typedef char hv_rfft_scalar_is_float[sizeof(kiss_fft_scalar) == sizeof(float) ? 1 : -1];

#ifdef __cplusplus
extern "C" {
#endif

hv_size_t sRFFT_init(SignalRFFT *o, const int size) {
  hv_assert(size >= (int) HV_N_SIMD);

  o->size = (hv_uint32_t) size;
  o->head = 0;
  o->blk = 0;

  hv_size_t numBytes = hTable_init(&o->input, size);
  numBytes += hTable_init(&o->outputReal, size * 2);
  numBytes += hTable_init(&o->outputImag, size * 2);
  numBytes += hTable_init(&o->scratch, size + 2); // (size/2+1) complex bins

  size_t len = 0;
  kiss_fftr_alloc(size, 0, NULL, &len); // query required size
  o->cfgFwd = hv_malloc(len);
  if (kiss_fftr_alloc(size, 0, o->cfgFwd, &len) == NULL) {
    o->cfgFwd = NULL;
  }
  return numBytes + (hv_size_t) len;
}

void sRFFT_free(SignalRFFT *o) {
  hTable_free(&o->input);
  hTable_free(&o->outputReal);
  hTable_free(&o->outputImag);
  hTable_free(&o->scratch);
  hv_free(o->cfgFwd);
  o->cfgFwd = NULL;
}

void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  const hv_uint32_t n = o->size;

  // release the spectrum of the previous block. The first block has no
  // predecessor, so it is silent: [rfft~] costs one block of latency.
  if (o->blk == 0) {
    __hv_zero_f(bOut0);
    __hv_zero_f(bOut1);
  } else {
    const hv_uint32_t offset = ((o->blk - 1) & 1) * n + o->head;
    __hv_load_f(o->outputReal.buffer + offset, bOut0);
    __hv_load_f(o->outputImag.buffer + offset, bOut1);
  }

  // accumulate
  __hv_store_f(o->input.buffer + o->head, bIn);
  o->head += HV_N_SIMD;

  if (o->head == n) {
    o->head = 0;

    // the slot was cleared on init and everything past bin size/2 is never
    // written again, so the tail of the block stays silent
    float *re = o->outputReal.buffer + (o->blk & 1) * n;
    float *im = o->outputImag.buffer + (o->blk & 1) * n;
    kiss_fft_cpx *sp = (kiss_fft_cpx *) o->scratch.buffer;

    if (o->cfgFwd != NULL) {
      kiss_fftr((kiss_fftr_cfg) o->cfgFwd, o->input.buffer, sp);
      for (hv_uint32_t k = 0; k <= n / 2; ++k) {
        re[k] = sp[k].r;
        im[k] = sp[k].i;
      }
    }
    o->blk++;
  }
}

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  (void) _c;
  (void) o;
  (void) m;
  (void) sendMessage;
  switch (letIndex) {
    default: return;
  }
}

hv_size_t sRIFFT_init(SignalRIFFT *o, const int size) {
  hv_assert(size >= (int) HV_N_SIMD);

  o->size = (hv_uint32_t) size;
  o->head = 0;
  o->blk = 0;

  hv_size_t numBytes = hTable_init(&o->inputReal, size);
  numBytes += hTable_init(&o->inputImag, size);
  numBytes += hTable_init(&o->output, size * 2);
  numBytes += hTable_init(&o->scratch, size + 2);

  size_t len = 0;
  kiss_fftr_alloc(size, 1, NULL, &len);
  o->cfgInv = hv_malloc(len);
  if (kiss_fftr_alloc(size, 1, o->cfgInv, &len) == NULL) {
    o->cfgInv = NULL;
  }
  return numBytes + (hv_size_t) len;
}

void sRIFFT_free(SignalRIFFT *o) {
  hTable_free(&o->inputReal);
  hTable_free(&o->inputImag);
  hTable_free(&o->output);
  hTable_free(&o->scratch);
  hv_free(o->cfgInv);
  o->cfgInv = NULL;
}

void __hv_rifft_f(SignalRIFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  const hv_uint32_t n = o->size;

  if (o->blk == 0) {
    __hv_zero_f(bOut);
  } else {
    __hv_load_f(o->output.buffer + ((o->blk - 1) & 1) * n + o->head, bOut);
  }

  __hv_store_f(o->inputReal.buffer + o->head, bIn0);
  __hv_store_f(o->inputImag.buffer + o->head, bIn1);
  o->head += HV_N_SIMD;

  if (o->head == n) {
    o->head = 0;

    kiss_fft_cpx *sp = (kiss_fft_cpx *) o->scratch.buffer;
    const float *re = o->inputReal.buffer;
    const float *im = o->inputImag.buffer;

    for (hv_uint32_t k = 0; k <= n / 2; ++k) {
      sp[k].r = re[k];
      sp[k].i = im[k];
    }
    // a real spectrum has no imaginary component at DC or Nyquist, and Pd
    // forcibly ignores whatever a patch writes there
    sp[0].i = 0.0f;
    sp[n / 2].i = 0.0f;

    if (o->cfgInv != NULL) {
      kiss_fftri((kiss_fftr_cfg) o->cfgInv, sp, o->output.buffer + (o->blk & 1) * n);
    }
    o->blk++;
  }
}

void sRIFFT_onMessage(HeavyContextInterface *_c, SignalRIFFT *o, int letIndex,
    const HvMessage *m, void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  (void) _c;
  (void) o;
  (void) m;
  (void) sendMessage;
  switch (letIndex) {
    default: return;
  }
}

#ifdef __cplusplus
} // extern "C"
#endif
