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

#ifndef _HEAVY_MATH_H_
#define _HEAVY_MATH_H_

#include "HvUtils.h"
#include <math.h>

static inline void __hv_zero_f(hv_bOutf_t bOut) {
  *bOut = 0.0f;
}

static inline void __hv_zero_i(hv_bOuti_t bOut) {
  *bOut = 0;
}

static inline void __hv_load_f(float *bIn, hv_bOutf_t bOut) {
  *bOut = *bIn;
}

static inline void __hv_store_f(float *bOut, hv_bInf_t bIn) {
  *bOut = bIn;
}

static inline void __hv_log2_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = 1.442695040888963f * hv_log_f(bIn);
}

// NOTE(mhroth): this is a pretty ghetto implementation
static inline void __hv_cos_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_cos_f(bIn);
}

static inline void __hv_acos_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_acos_f(bIn);
}

static inline void __hv_cosh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_cosh_f(bIn);
}

static inline void __hv_acosh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_acosh_f(bIn);
}

static inline void __hv_sin_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_sin_f(bIn);
}

static inline void __hv_asin_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_asin_f(bIn);
}

static inline void __hv_sinh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_sinh_f(bIn);
}

static inline void __hv_asinh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_asinh_f(bIn);
}

static inline void __hv_tan_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_tan_f(bIn);
}

static inline void __hv_atan_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_atan_f(bIn);
}

static inline void __hv_atan2_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_atan2_f(bIn0, bIn1);
}

static inline void __hv_tanh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_tanh_f(bIn);
}

static inline void __hv_atanh_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_atanh_f(bIn);
}

static inline void __hv_sqrt_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_sqrt_f(bIn);
}

static inline void __hv_rsqrt_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = 1.0f/hv_sqrt_f(bIn);
}

static inline void __hv_abs_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_abs_f(bIn);
}

static inline void __hv_neg_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = bIn * -1.0f;
}

static inline void __hv_exp_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_exp_f(bIn);
}

static inline void __hv_expm1_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_expm1_f(bIn);
}

static inline void __hv_ceil_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_ceil_f(bIn);
}

static inline void __hv_floor_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_floor_f(bIn);
}

// __add~f
static inline void __hv_add_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = bIn0 + bIn1;
}

// __add~i
static inline void __hv_add_i(hv_bIni_t bIn0, hv_bIni_t bIn1, hv_bOuti_t bOut) {
  *bOut = bIn0 + bIn1;
}

// __sub~f
static inline void __hv_sub_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = bIn0 - bIn1;
}

// __mul~f
static inline void __hv_mul_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = bIn0 * bIn1;
}

// __*~i
static inline void __hv_mul_i(hv_bIni_t bIn0, hv_bIni_t bIn1, hv_bOuti_t bOut) {
  *bOut = bIn0 * bIn1;
}

// __cast~if
static inline void __hv_cast_if(hv_bIni_t bIn, hv_bOutf_t bOut) {
  *bOut = (float) bIn;
}

// __cast~fi
static inline void __hv_cast_fi(hv_bInf_t bIn, hv_bOuti_t bOut) {
  *bOut = (int) bIn;
}

// expr~ expects all float i/o
static inline void __hv_cast_if_expr(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = (float) bIn;
}

// expr~ expects all float i/o
static inline void __hv_cast_fi_expr(hv_bInf_t bIn, hv_bOutf_t bOut) {
  if (bIn < 0.0f) *bOut = hv_rint_f(bIn);
  else if (bIn > 0.0f) *bOut = hv_floor_f(bIn);
  else *bOut = 0.0f;
}

static inline void __hv_div_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn1 != 0.0f) ? (bIn0 / bIn1) : 0.0f;
}

static inline void __hv_min_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_min_f(bIn0, bIn1);
}

static inline void __hv_min_i(hv_bIni_t bIn0, hv_bIni_t bIn1, hv_bOuti_t bOut) {
  *bOut = hv_min_i(bIn0, bIn1);
}

static inline void __hv_max_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_max_f(bIn0, bIn1);
}

static inline void __hv_max_i(hv_bIni_t bIn0, hv_bIni_t bIn1, hv_bOuti_t bOut) {
  *bOut = hv_max_i(bIn0, bIn1);
}

static inline void __hv_pow_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_pow_f(bIn0, bIn1);
}

static inline void __hv_gt_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 > bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_gte_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 >= bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_lt_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 < bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_lte_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 <= bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_eq_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 == bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_neq_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0 != bIn1) ? 1.0f : 0.0f;
}

static inline void __hv_or_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  if (bIn0 == 0.0f && bIn1 == 0.0f) *bOut = 0.0f;
  else if (bIn0 == 0.0f) *bOut = bIn1;
  else if (bIn1 == 0.0f) *bOut = bIn0;
  else hv_assert(0);
}

static inline void __hv_and_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  if (bIn0 == 0.0f || bIn1 == 0.0f) *bOut = 0.0f;
  else if (bIn0 == 1.0f) *bOut = bIn1;
  else if (bIn1 == 1.0f) *bOut = bIn0;
  else hv_assert(0);
}

static inline void __hv_not_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_not_f(bIn);
}

static inline void __hv_andnot_f(hv_bInf_t bIn0_mask, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (bIn0_mask == 0.0f) ? bIn1 : 0.0f;
}

// bOut = (bIn0 * bIn1) + bIn2
static inline void __hv_fma_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bInf_t bIn2, hv_bOutf_t bOut) {
  *bOut = hv_fma_f(bIn0, bIn1, bIn2);
}

// bOut = (bIn0 * bIn1) - bIn2
static inline void __hv_fms_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bInf_t bIn2, hv_bOutf_t bOut) {
  *bOut = (bIn0 * bIn1) - bIn2;
}

static inline void __hv_cbrt_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_cbrt_f(bIn);
}

static inline void __hv_erf_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_erf_f(bIn);
}

static inline void __hv_erfc_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_erfc_f(bIn);
}

static inline void __hv_ln_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_ln_f(bIn);
}

static inline void __hv_log_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_log_f(bIn);
}

static inline void __hv_log1p_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_log1p_f(bIn);
}

static inline void __hv_log10_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_log10_f(bIn);
}

static inline void __hv_modf_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_modf_f(bIn);
}

static inline void __hv_modulo_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  float modded = hv_fmod_f(bIn0, bIn1);
  if (modded < 0.0f) *bOut = hv_rint_f(modded);
  else if (modded >= 0.0f) *bOut = hv_floor_f(modded);
}

static inline void __hv_shl_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (float) hv_shl_i((int) bIn0, (int) bIn1);
}

static inline void __hv_shr_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (float) hv_shr_i((int) bIn0, (int) bIn1);
}

static inline void __hv_bit_and_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (float) ((int) bIn0 & (int) bIn1);
}

static inline void __hv_bit_or_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (float) ((int) bIn0 | (int) bIn1);
}

static inline void __hv_bit_not_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = (float) hv_bit_not_i((int) bIn);
}

static inline void __hv_exc_or_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = (float) ((int) bIn0 ^ (int) bIn1);
}

static inline void __hv_log_and_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = bIn0 && bIn1;
}

static inline void __hv_log_or_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = bIn0 || bIn1;
}

static inline void __hv_rint_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_rint_f(bIn);
}

static inline void __hv_round_f(hv_bInf_t bIn, hv_bOutf_t bOut) {
  *bOut = hv_round_f(bIn);
}

static inline void __hv_if_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bInf_t bIn2, hv_bOutf_t bOut) {
  *bOut = hv_if_f(bIn0, bIn1, bIn2);
}

static inline void __hv_isinf_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  *bOut = hv_isinf_f(bIn0);
}

static inline void __hv_finite_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  *bOut = hv_finite_f(bIn0);
}

static inline void __hv_isnan_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  *bOut = hv_isnan_f(bIn0);
}

static inline void __hv_copysign_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_copysign_f(bIn0, bIn1);
}

static inline void __hv_imod_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  float iptr;
  modff(bIn0, &iptr);
  *bOut = iptr;
}

static inline void __hv_remainder_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_remainder_f(bIn0, bIn1);
}

static inline void __hv_fmod_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_fmod_f(bIn0, bIn1);
}

static inline void __hv_fact_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  int n = (int) bIn0;
  if(n <= 1) {
    // follow Pure data convention
    *bOut = 1;
  }
  else if(n > 34) {
    // follow Pure data convention
    *bOut = INFINITY; // C99 constant
  }
  else {
    float f = 1.0f;
    for (int i = n; i > 1; --i) {
      f *= i;
    }
    *bOut = f;
  }
}

static inline void __hv_ldexp_f(hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  *bOut = hv_ldexp_f(bIn0, bIn1);
}

static inline void __hv_bitsafe_f(hv_bInf_t bIn0, hv_bOutf_t bOut) {
  if (hv_isnan_f(bIn0) || hv_isinf_f(bIn0))
    *bOut = 0.0f;
  else
    *bOut = bIn0;
}

#endif // _HEAVY_MATH_H_
