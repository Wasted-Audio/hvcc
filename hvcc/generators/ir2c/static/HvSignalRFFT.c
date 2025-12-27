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

hv_size_t sRFFT_init(SignalRFFT *o, const int size) {
  hv_size_t numBytes = hTable_init(&o->input, size);
  numBytes += hTable_init(&o->outputReal, size/2+1);
  numBytes += hTable_init(&o->outputImagin, size/2+1);
  return numBytes;
}

void sRFFT_free(SignalRFFT *o) {
  hTable_free(&o->input);
  hTable_free(&o->outputReal);
  hTable_free(&o->outputImagin);
}

void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  // do fft stuff
}

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    default: return;
  }
}

hv_size_t sRIFFT_init(SignalRIFFT *o, const int size) {
  hv_size_t numBytes = hTable_init(&o->inputReal, size/2+1);
  numBytes += hTable_init(&o->inputImagin, size/2+1);
  numBytes += hTable_init(&o->output, size);
  return numBytes;
}

void sRIFFT_free(SignalRIFFT *o) {
  hTable_free(&o->inputReal);
  hTable_free(&o->inputImagin);
  hTable_free(&o->output);
}

void __hv_rifft_f(SignalRIFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
   // do ifft stuff
}

void sRIFFT_onMessage(HeavyContextInterface *_c, SignalRIFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    default: return;
  }
}
