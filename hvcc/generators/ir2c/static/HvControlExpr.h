/**
 * Copyright (c) 2022-2025 Daniel Billotte, Wasted Audio
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

#ifndef _HEAVY_CONTROL_EXPR_H_
#define _HEAVY_CONTROL_EXPR_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_EXPR_ARGS 100

typedef struct ControlExpr {
  float args[MAX_EXPR_ARGS];
  float(*eval_fptr)(const float*);
} ControlExpr;

hv_size_t cExpr_init(ControlExpr *o, float(*eval_fptr)(const float*));

void cExpr_free(ControlExpr *o);

void cExpr_onMessage(HeavyContextInterface *_c, ControlExpr *o, int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));

float expr_modf(float mod);

float expr_imodf(float mod);

float expr_if(float eval, float trueValue, float falseValue);

float expr_fact(float factor);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_CONTROL_EXPR_H_
