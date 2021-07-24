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

#ifndef _HEAVY_CONTROL_BINOP_H_
#define _HEAVY_CONTROL_BINOP_H_

#include "HvHeavyInternal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum BinopType {
  HV_BINOP_ADD,
  HV_BINOP_SUBTRACT,
  HV_BINOP_MULTIPLY,
  HV_BINOP_DIVIDE,
  HV_BINOP_INT_DIV,
  HV_BINOP_MOD_BIPOLAR,
  HV_BINOP_MOD_UNIPOLAR,
  HV_BINOP_BIT_LEFTSHIFT,
  HV_BINOP_BIT_RIGHTSHIFT,
  HV_BINOP_BIT_AND,
  HV_BINOP_BIT_XOR,
  HV_BINOP_BIT_OR,
  HV_BINOP_EQ,
  HV_BINOP_NEQ,
  HV_BINOP_LOGICAL_AND,
  HV_BINOP_LOGICAL_OR,
  HV_BINOP_LESS_THAN,
  HV_BINOP_LESS_THAN_EQL,
  HV_BINOP_GREATER_THAN,
  HV_BINOP_GREATER_THAN_EQL,
  HV_BINOP_MAX,
  HV_BINOP_MIN,
  HV_BINOP_POW,
  HV_BINOP_ATAN2
} BinopType;

typedef struct ControlBinop {
  float k;
} ControlBinop;

hv_size_t cBinop_init(ControlBinop *o, float k);

void cBinop_onMessage(HeavyContextInterface *_c, ControlBinop *o, BinopType op, int letIn,
    const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));

void cBinop_k_onMessage(HeavyContextInterface *_c, void *o, BinopType op, float k,
    int letIn, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *));

#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_CONTROL_BINOP_H_
