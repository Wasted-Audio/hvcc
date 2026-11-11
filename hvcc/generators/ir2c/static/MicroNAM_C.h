#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

// Opaque handles for the different network types
typedef struct MicroNAM_NanoNet MicroNAM_NanoNet;
typedef struct MicroNAM_FeatherNet MicroNAM_FeatherNet;
typedef struct MicroNAM_LiteNet MicroNAM_LiteNet;
typedef struct MicroNAM_StandardNet MicroNAM_StandardNet;
typedef struct MicroNAM_A2LiteNet MicroNAM_A2LiteNet;
typedef struct MicroNAM_A2FullNet MicroNAM_A2FullNet;

// --- NanoNet API ---
MicroNAM_NanoNet* MicroNAM_NanoNet_Create(void);
void MicroNAM_NanoNet_Destroy(MicroNAM_NanoNet* net);
void MicroNAM_NanoNet_Reset(MicroNAM_NanoNet* net);
void MicroNAM_NanoNet_LoadWeights(MicroNAM_NanoNet* net, const float* weights);
void MicroNAM_NanoNet_Process(MicroNAM_NanoNet* net, float* input, float* output);

// --- FeatherNet API ---
MicroNAM_FeatherNet* MicroNAM_FeatherNet_Create(void);
void MicroNAM_FeatherNet_Destroy(MicroNAM_FeatherNet* net);
void MicroNAM_FeatherNet_Reset(MicroNAM_FeatherNet* net);
void MicroNAM_FeatherNet_LoadWeights(MicroNAM_FeatherNet* net, const float* weights);
void MicroNAM_FeatherNet_Process(MicroNAM_FeatherNet* net, float* input, float* output);

// --- LiteNet API ---
MicroNAM_LiteNet* MicroNAM_LiteNet_Create(void);
void MicroNAM_LiteNet_Destroy(MicroNAM_LiteNet* net);
void MicroNAM_LiteNet_Reset(MicroNAM_LiteNet* net);
void MicroNAM_LiteNet_LoadWeights(MicroNAM_LiteNet* net, const float* weights);
void MicroNAM_LiteNet_Process(MicroNAM_LiteNet* net, float* input, float* output);

// --- StandardNet API ---
MicroNAM_StandardNet* MicroNAM_StandardNet_Create(void);
void MicroNAM_StandardNet_Destroy(MicroNAM_StandardNet* net);
void MicroNAM_StandardNet_Reset(MicroNAM_StandardNet* net);
void MicroNAM_StandardNet_LoadWeights(MicroNAM_StandardNet* net, const float* weights);
void MicroNAM_StandardNet_Process(MicroNAM_StandardNet* net, float* input, float* output);

// --- A2 Lite API ---
MicroNAM_A2LiteNet* MicroNAM_A2LiteNet_Create(void);
void MicroNAM_A2LiteNet_Destroy(MicroNAM_A2LiteNet* net);
void MicroNAM_A2LiteNet_Reset(MicroNAM_A2LiteNet* net);
void MicroNAM_A2LiteNet_LoadWeights(MicroNAM_A2LiteNet* net, const float* weights);
void MicroNAM_A2LiteNet_Process(MicroNAM_A2LiteNet* net, float* input, float* output);
void MicroNAM_A2LiteNet_ProcessBlock(MicroNAM_A2LiteNet* net, const float* input, float* output, int n);

// --- A2 Full API ---
MicroNAM_A2FullNet* MicroNAM_A2FullNet_Create(void);
void MicroNAM_A2FullNet_Destroy(MicroNAM_A2FullNet* net);
void MicroNAM_A2FullNet_Reset(MicroNAM_A2FullNet* net);
void MicroNAM_A2FullNet_LoadWeights(MicroNAM_A2FullNet* net, const float* weights);
void MicroNAM_A2FullNet_Process(MicroNAM_A2FullNet* net, float* input, float* output);


#ifdef __cplusplus
}
#endif
