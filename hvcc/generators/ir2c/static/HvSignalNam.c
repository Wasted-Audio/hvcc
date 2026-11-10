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

#include "HvSignalNam.h"

hv_size_t sNam_nano_init(SignalNamNano *o, const float* weights) {
  MicroNAM_NanoNet* nanonet = MicroNAM_NanoNet_Create();
  MicroNAM_NanoNet_LoadWeights(nanonet, weights);
  o->nanonet = nanonet;
  return sizeof(float) * 842;
}

void sNam_nano_free(SignalNamNano *o) {
  MicroNAM_NanoNet_Destroy(o->nanonet);
}


hv_size_t sNam_feather_init(SignalNamFeather *o, const float* weights) {
  MicroNAM_FeatherNet* feathernet = MicroNAM_FeatherNet_Create();
  MicroNAM_FeatherNet_LoadWeights(feathernet, weights);
  o->feathernet = feathernet;
  return sizeof(float) * 3026;
}

void sNam_feather_free(SignalNamFeather *o) {
  MicroNAM_FeatherNet_Destroy(o->feathernet);
}


hv_size_t sNam_lite_init(SignalNamLite *o, const float* weights) {
  MicroNAM_LiteNet* litenet = MicroNAM_LiteNet_Create();
  MicroNAM_LiteNet_LoadWeights(litenet, weights);
  o->litenet = litenet;
  return sizeof(float) * 6554;
}

void sNam_lite_free(SignalNamLite *o) {
  MicroNAM_LiteNet_Destroy(o->litenet);
}


hv_size_t sNam_standard_init(SignalNamStandard *o, const float* weights) {
  MicroNAM_StandardNet* standardnet = MicroNAM_StandardNet_Create();
  MicroNAM_StandardNet_LoadWeights(standardnet, weights);
  o->standardnet = standardnet;
  return sizeof(float) * 13802;
}

void sNam_standard_free(SignalNamStandard *o) {
  MicroNAM_StandardNet_Destroy(o->standardnet);
}
