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

#ifndef _HEAVY_SIGNAL_TABREAD_H_
#define _HEAVY_SIGNAL_TABREAD_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalTabread {
  HvTable *table; // the table to read
  hv_uint32_t head;
  bool forceAlignedLoads; // false by default, true if using __hv_tabread_f
} SignalTabread;

// random access to a table
hv_size_t sTabread_init(SignalTabread *o, HvTable *table, bool forceAlignedLoads);



#if HV_APPLE
#pragma mark - Tabread - Random Access
#endif

static inline void __hv_tabread_if(SignalTabread *o, hv_bIni_t bIn, hv_bOutf_t bOut) {
  const float *const b = hTable_getBuffer(o->table);
#if HV_SIMD_AVX
  const hv_int32_t *const i = (hv_int32_t *) &bIn;

  hv_assert(i[0] >= 0 && i[0] < hTable_getAllocated(o->table));
  hv_assert(i[1] >= 0 && i[1] < hTable_getAllocated(o->table));
  hv_assert(i[2] >= 0 && i[2] < hTable_getAllocated(o->table));
  hv_assert(i[3] >= 0 && i[3] < hTable_getAllocated(o->table));
  hv_assert(i[4] >= 0 && i[4] < hTable_getAllocated(o->table));
  hv_assert(i[5] >= 0 && i[5] < hTable_getAllocated(o->table));
  hv_assert(i[6] >= 0 && i[6] < hTable_getAllocated(o->table));
  hv_assert(i[7] >= 0 && i[7] < hTable_getAllocated(o->table));

  *bOut = _mm256_set_ps(b[i[7]], b[i[6]], b[i[5]], b[i[4]], b[i[3]], b[i[2]], b[i[1]], b[i[0]]);
#elif HV_SIMD_SSE
  const hv_int32_t *const i = (hv_int32_t *) &bIn;

  hv_assert(i[0] >= 0 && ((hv_uint32_t) i[0]) < hTable_getAllocated(o->table));
  hv_assert(i[1] >= 0 && ((hv_uint32_t) i[1]) < hTable_getAllocated(o->table));
  hv_assert(i[2] >= 0 && ((hv_uint32_t) i[2]) < hTable_getAllocated(o->table));
  hv_assert(i[3] >= 0 && ((hv_uint32_t) i[3]) < hTable_getAllocated(o->table));

  *bOut = _mm_set_ps(b[i[3]], b[i[2]], b[i[1]], b[i[0]]);
#elif HV_SIMD_NEON
  hv_assert((bIn[0] >= 0) && (bIn[0] < hTable_getAllocated(o->table)));
  hv_assert((bIn[1] >= 0) && (bIn[1] < hTable_getAllocated(o->table)));
  hv_assert((bIn[2] >= 0) && (bIn[2] < hTable_getAllocated(o->table)));
  hv_assert((bIn[3] >= 0) && (bIn[3] < hTable_getAllocated(o->table)));

  *bOut = (float32x4_t) {b[bIn[0]], b[bIn[1]], b[bIn[2]], b[bIn[3]]};
#else // HV_SIMD_NONE
  hv_assert(bIn >= 0 && ((hv_uint32_t) bIn < hTable_getAllocated(o->table)));

  *bOut = b[bIn];
#endif
}



#if HV_APPLE
#pragma mark - Tabread - Linear Access
#endif

// this tabread never stops reading. It is mainly intended for linear reads that loop around a table.
static inline void __hv_tabread_f(SignalTabread *o, hv_bOutf_t bOut) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getAllocated(o->table)); // assert that we always read within the table bounds
  hv_uint32_t head = o->head;
#if HV_SIMD_AVX
  *bOut = _mm256_load_ps(hTable_getBuffer(o->table) + head);
#elif HV_SIMD_SSE
  *bOut = _mm_load_ps(hTable_getBuffer(o->table) + head);
#elif HV_SIMD_NEON
  *bOut = vld1q_f32(hTable_getBuffer(o->table) + head);
#else // HV_SIMD_NONE
  *bOut = *(hTable_getBuffer(o->table) + head);
#endif
  o->head = head + HV_N_SIMD;
}

// unaligned linear tabread, as above
static inline void __hv_tabreadu_f(SignalTabread *o, hv_bOutf_t bOut) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getAllocated(o->table)); // assert that we always read within the table bounds
  hv_uint32_t head = o->head;
#if HV_SIMD_AVX
  *bOut = _mm256_loadu_ps(hTable_getBuffer(o->table) + head);
#elif HV_SIMD_SSE
  *bOut = _mm_loadu_ps(hTable_getBuffer(o->table) + head);
#elif HV_SIMD_NEON
  *bOut = vld1q_f32(hTable_getBuffer(o->table) + head);
#else // HV_SIMD_NONE
  *bOut = *(hTable_getBuffer(o->table) + head);
#endif
  o->head = head + HV_N_SIMD;
}

// this tabread can be instructed to stop. It is mainly intended for linear reads that only process a portion of a buffer.
static inline void __hv_tabread_stoppable_f(SignalTabread *o, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  if (o->head == ~0x0) {
    *bOut = _mm256_setzero_ps();
  } else {
    *bOut = _mm256_load_ps(hTable_getBuffer(o->table) + o->head);
    o->head += HV_N_SIMD;
  }
#elif HV_SIMD_SSE
  if (o->head == ~0x0) {
    *bOut = _mm_setzero_ps();
  } else {
    *bOut = _mm_load_ps(hTable_getBuffer(o->table) + o->head);
    o->head += HV_N_SIMD;
  }
#elif HV_SIMD_NEON
  if (o->head == ~0x0) {
    *bOut = vdupq_n_f32(0.0f);
  } else {
    *bOut = vld1q_f32(hTable_getBuffer(o->table) + o->head);
    o->head += HV_N_SIMD;
  }
#else // HV_SIMD_NONE
  if (o->head == ~0x0) {
    *bOut = 0.0f;
  } else {
    *bOut = *(hTable_getBuffer(o->table) + o->head);
    o->head += HV_N_SIMD;
  }
#endif
}

void sTabread_onMessage(HeavyContextInterface *_c, SignalTabread *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));



#if HV_APPLE
#pragma mark - Tabhead
#endif

typedef struct SignalTabhead {
  HvTable *table;
} SignalTabhead;

hv_size_t sTabhead_init(SignalTabhead *o, HvTable *table);

static inline void __hv_tabhead_f(SignalTabhead *o, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  *bOut = _mm256_set1_ps((float) hTable_getHead(o->table));
#elif HV_SIMD_SSE
  *bOut = _mm_set1_ps((float) hTable_getHead(o->table));
#elif HV_SIMD_NEON
  *bOut = vdupq_n_f32((float32_t) hTable_getHead(o->table));
#else // HV_SIMD_NONE
  *bOut = (float) hTable_getHead(o->table);
#endif
}

void sTabhead_onMessage(HeavyContextInterface *_c, SignalTabhead *o, const HvMessage *m);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABREAD_H_
