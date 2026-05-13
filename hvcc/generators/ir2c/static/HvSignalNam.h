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

#ifndef _SIGNAL_LORENZ_H_
#define _SIGNAL_LORENZ_H_

#include "HvHeavyInternal.h"
#include "MicroNAM_C.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SignalNamNano {
  MicroNAM_NanoNet* nanonet;
} SignalNamNano;

hv_size_t sNam_nano_init(SignalNamNano *o, const float* weights);
void sNam_nano_free(SignalNamNano *o);

static inline void __hv_nam_nano_f(SignalNamNano *o, hv_bInf_t bIn0, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_assert(0);
#elif HV_SIMD_SSE
  hv_assert(0);
#elif HV_SIMD_NEON
  hv_assert(0);
#else // HV_SIMD_NONE
  MicroNAM_NanoNet_Process(o->nanonet, &bIn0, bOut);
#endif
}


typedef struct SignalNamFeather {
  MicroNAM_FeatherNet* feathernet;
} SignalNamFeather;

hv_size_t sNam_feather_init(SignalNamFeather *o, const float* weights);
void sNam_feather_free(SignalNamFeather *o);

static inline void __hv_nam_feather_f(SignalNamFeather *o, hv_bInf_t bIn0, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_assert(0);
#elif HV_SIMD_SSE
  hv_assert(0);
#elif HV_SIMD_NEON
  hv_assert(0);
#else // HV_SIMD_NONE
  MicroNAM_FeatherNet_Process(o->feathernet, &bIn0, bOut);
#endif
}


typedef struct SignalNamLite {
  MicroNAM_LiteNet* litenet;
} SignalNamLite;

hv_size_t sNam_lite_init(SignalNamLite *o, const float* weights);
void sNam_lite_free(SignalNamLite *o);

static inline void __hv_nam_lite_f(SignalNamLite *o, hv_bInf_t bIn0, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_assert(0);
#elif HV_SIMD_SSE
  hv_assert(0);
#elif HV_SIMD_NEON
  hv_assert(0);
#else // HV_SIMD_NONE
    MicroNAM_LiteNet_Process(o->litenet, &bIn0, bOut);
#endif
}


typedef struct SignalNamStandard {
  MicroNAM_StandardNet* standardnet;
} SignalNamStandard;

hv_size_t sNam_standard_init(SignalNamStandard *o, const float* weights);
void sNam_standard_free(SignalNamStandard *o);

static inline void __hv_nam_standard_f(SignalNamStandard *o, hv_bInf_t bIn0, hv_bOutf_t bOut) {
#if HV_SIMD_AVX
  hv_assert(0);
#elif HV_SIMD_SSE
  hv_assert(0);
#elif HV_SIMD_NEON
  hv_assert(0);
#else // HV_SIMD_NONE
  MicroNAM_StandardNet_Process(o->standardnet, &bIn0, bOut);
#endif
}


#ifdef __cplusplus
} // extern "C"
#endif

#endif // _SIGNAL_LORENZ_H_
