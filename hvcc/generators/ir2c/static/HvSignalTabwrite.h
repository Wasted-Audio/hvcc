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

#ifndef _HEAVY_SIGNAL_TABWRITE_H_
#define _HEAVY_SIGNAL_TABWRITE_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HV_TABWRITE_STOPPED -1 // ~0x0

typedef struct SignalTabwrite {
  HvTable *table;
  hv_uint32_t head; // local write head. Where this object has most recently written to the table.
} SignalTabwrite;

hv_size_t sTabwrite_init(SignalTabwrite *o, HvTable *table);

void sTabwrite_onMessage(HeavyContextInterface *_c, SignalTabwrite *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));

// linear write to table
static inline void __hv_tabwrite_f(SignalTabwrite *o, hv_bInf_t bIn) {
  hv_assert((o->head + HV_N_SIMD) <= hTable_getSize(o->table)); // assert that the table bounds are respected
  hv_uint32_t head = o->head;
#if HV_SIMD_AVX
  _mm256_store_ps(hTable_getBuffer(o->table) + head, bIn);
#elif HV_SIMD_SSE
  _mm_store_ps(hTable_getBuffer(o->table) + head, bIn);
#elif HV_SIMD_NEON
  vst1q_f32(hTable_getBuffer(o->table) + head, bIn);
#else // HV_SIMD_NONE
  *(hTable_getBuffer(o->table) + head) = bIn;
#endif
  head += HV_N_SIMD;
  o->head = head; // update local write head
  hTable_setHead(o->table, head); // update the remote write head (e.g. for use by vd~)
}

// linear unaligned write to table
static inline void __hv_tabwriteu_f(SignalTabwrite *o, hv_bInf_t bIn) {
  hv_uint32_t head = o->head;
#if HV_SIMD_AVX
  _mm256_storeu_ps(hTable_getBuffer(o->table) + head, bIn);
#elif HV_SIMD_SSE
  _mm_storeu_ps(hTable_getBuffer(o->table) + head, bIn);
#elif HV_SIMD_NEON
  vst1q_f32(hTable_getBuffer(o->table) + head, bIn);
#else // HV_SIMD_NONE
  *(hTable_getBuffer(o->table) + head) = bIn;
#endif
  head += HV_N_SIMD;
  o->head = head; // update local write head
  hTable_setHead(o->table, head); // update remote write head
}

// this tabread can be instructed to stop. It is mainly intended for linear reads that only process a portion of a buffer.
// Stores are unaligned, which can be slow but allows any indicies to be written to.
// TODO(mhroth): this is not stopping!
static inline void __hv_tabwrite_stoppable_f(SignalTabwrite *o, hv_bInf_t bIn) {
  if (o->head != HV_TABWRITE_STOPPED) {
#if HV_SIMD_AVX
    _mm256_storeu_ps(hTable_getBuffer(o->table) + o->head, bIn);
#elif HV_SIMD_SSE
    _mm_storeu_ps(hTable_getBuffer(o->table) + o->head, bIn);
#elif HV_SIMD_NEON
    vst1q_f32(hTable_getBuffer(o->table) + o->head, bIn);
#else // HV_SIMD_NONE
    *(hTable_getBuffer(o->table) + o->head) = bIn;
#endif
    o->head += HV_N_SIMD;
  }
}

// random write to table
static inline void __hv_tabwrite_if(SignalTabwrite *o, hv_bIni_t bIn0, hv_bInf_t bIn1) {
  float *const b = hTable_getBuffer(o->table);
#if HV_SIMD_AVX
  const hv_int32_t *const i = (hv_int32_t *) &bIn0;
  const float *const f = (float *) &bIn1;

  hv_assert(i[0] >= 0 && i[0] < hTable_getAllocated(o->table));
  hv_assert(i[1] >= 0 && i[1] < hTable_getAllocated(o->table));
  hv_assert(i[2] >= 0 && i[2] < hTable_getAllocated(o->table));
  hv_assert(i[3] >= 0 && i[3] < hTable_getAllocated(o->table));
  hv_assert(i[4] >= 0 && i[4] < hTable_getAllocated(o->table));
  hv_assert(i[5] >= 0 && i[5] < hTable_getAllocated(o->table));
  hv_assert(i[6] >= 0 && i[6] < hTable_getAllocated(o->table));
  hv_assert(i[7] >= 0 && i[7] < hTable_getAllocated(o->table));

  b[i[0]] = f[0];
  b[i[1]] = f[1];
  b[i[2]] = f[2];
  b[i[3]] = f[3];
  b[i[4]] = f[4];
  b[i[5]] = f[5];
  b[i[6]] = f[6];
  b[i[7]] = f[7];
#elif HV_SIMD_SSE
  const hv_int32_t *const i = (hv_int32_t *) &bIn0;
  const float *const f = (float *) &bIn1;

  hv_assert(i[0] >= 0 && ((hv_uint32_t) i[0]) < hTable_getAllocated(o->table));
  hv_assert(i[1] >= 0 && ((hv_uint32_t) i[1]) < hTable_getAllocated(o->table));
  hv_assert(i[2] >= 0 && ((hv_uint32_t) i[2]) < hTable_getAllocated(o->table));
  hv_assert(i[3] >= 0 && ((hv_uint32_t) i[3]) < hTable_getAllocated(o->table));

  b[i[0]] = f[0];
  b[i[1]] = f[1];
  b[i[2]] = f[2];
  b[i[3]] = f[3];
#elif HV_SIMD_NEON
  hv_assert((vgetq_lane_s32(bIn0,0) >= 0) && (vgetq_lane_s32(bIn0,0) < hTable_getSize(o->table)));
  hv_assert((vgetq_lane_s32(bIn0,1) >= 0) && (vgetq_lane_s32(bIn0,1) < hTable_getSize(o->table)));
  hv_assert((vgetq_lane_s32(bIn0,2) >= 0) && (vgetq_lane_s32(bIn0,2) < hTable_getSize(o->table)));
  hv_assert((vgetq_lane_s32(bIn0,3) >= 0) && (vgetq_lane_s32(bIn0,3) < hTable_getSize(o->table)));

  vst1q_lane_f32(b + vgetq_lane_s32(bIn0, 0), bIn1, 0);
  vst1q_lane_f32(b + vgetq_lane_s32(bIn0, 1), bIn1, 1);
  vst1q_lane_f32(b + vgetq_lane_s32(bIn0, 2), bIn1, 2);
  vst1q_lane_f32(b + vgetq_lane_s32(bIn0, 3), bIn1, 3);
#else // HV_SIMD_NONE
  b[bIn0] = bIn1;
#endif
}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_SIGNAL_TABWRITE_H_
