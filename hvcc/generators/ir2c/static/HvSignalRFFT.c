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

hv_size_t sRFFT_init(SignalRFFT *o, struct HvTable *table, const int size) {
  o->table = table;
  hv_size_t numBytes = hTable_init(&o->inputs, size);
  return numBytes;
}

void sRFFT_free(SignalRFFT *o) {
  o->table = NULL;
  hTable_free(&o->inputs);
}

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    case 1: {
      if (msg_isHashLike(m,0)) {
        HvTable *table = hv_table_get(_c, msg_getHash(m,0));
        if (table != NULL) {
          o->table = table;
          if (hTable_getSize(&o->inputs) != hTable_getSize(table)) {
            hTable_resize(&o->inputs,
                (hv_uint32_t) hv_min_ui(hTable_getSize(&o->inputs), hTable_getSize(table)));
          }
        }
      }
      break;
    }
    case 2: {
      if (msg_isFloat(m,0)) {
        // rfft size should never exceed the coefficient table size
        hTable_resize(&o->inputs, (hv_uint32_t) msg_getFloat(m,0));
      }
      break;
    }
    default: return;
  }
}


static inline int wrap(const int i, const int n) {
  if (i < 0) return (i+n);
  if (i >= n) return (i-n);
  return i;
}


void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  hv_assert(o->table != NULL);
  float *const work = hTable_getBuffer(o->table);
  hv_assert(work != NULL);
  const int n = hTable_getSize(o->table); // length fir filter
  hv_assert((n&HV_N_SIMD_MASK) == 0); // n is a multiple of HV_N_SIMD

  float *const inputs = hTable_getBuffer(&o->inputs);
  hv_assert(inputs != NULL);
  const int m = hTable_getSize(&o->inputs); // length of input buffer.
  hv_assert(m >= n);
  const int h_orig = hTable_getHead(&o->inputs);

  // float *const bOut = (float *)(hv_alloca(2*n*sizeof(float)));
  float *const bOut = (float *)(hv_alloca(sizeof(bIn)));

  // do fft stuff

  // uninterleave result into the output buffers
  for (int j = 0; j < n; ++j) {
    bOut0[n+j] = bOut[0+2*j];
    bOut1[n+j] = bOut[1+2*j];
  }

  __hv_store_f(inputs+h_orig, bIn); // store the new input to the inputs buffer
  hTable_setHead(&o->inputs, wrap(h_orig+HV_N_SIMD, m));
}


void __hv_rifft_f(SignalRFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  hv_assert(o->table != NULL);
  float *const work = hTable_getBuffer(o->table);
  hv_assert(work != NULL);
  const int n = hTable_getSize(o->table); // length fir filter
  hv_assert((n&HV_N_SIMD_MASK) == 0); // n is a multiple of HV_N_SIMD

  float *const inputs = hTable_getBuffer(&o->inputs);
  hv_assert(inputs != NULL);
  const int m = hTable_getSize(&o->inputs); // length of input buffer.
  hv_assert(m >= n);
  const int h_orig = hTable_getHead(&o->inputs);

  float *bIn00 = &bIn0;
  float *bIn10 = &bIn1;
  // float *const bIn = (float *)(hv_alloca(2*n*sizeof(float)));
  float *const bIn = (float *)(hv_alloca(sizeof(bOut)));

  // interleave the input buffers into the transform buffer
  for (int i = 0; i < 2; ++i) {
    for (int j = 0; j < n; ++j) {
      bIn[0+2*j] = bIn00[n+j];
      bIn[1+2*j] = bIn10[n+j];
    }
  }

  // do ifft stuff

  // __hv_store_f(inputs+h_orig, bIn); // store the new input to the inputs buffer
  hTable_setHead(&o->inputs, wrap(h_orig+HV_N_SIMD, m));
}
