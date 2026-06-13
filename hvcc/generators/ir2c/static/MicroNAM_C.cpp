#include "MicroNAM_C.h"
#include "MicroNam/MicroNAM.h"
#include <new>

// We use a block size of 1 for single-sample processing
#define NAM_BLOCK_SIZE 1

using namespace MicroNAM;

#ifdef __cplusplus
extern "C" {
#endif

// --- NanoNet ---

MicroNAM_NanoNet* MicroNAM_NanoNet_Create(void) {
    return reinterpret_cast<MicroNAM_NanoNet*>(new (std::nothrow) NanoNet<NAM_BLOCK_SIZE>());
}

void MicroNAM_NanoNet_Destroy(MicroNAM_NanoNet* net) {
    delete reinterpret_cast<NanoNet<NAM_BLOCK_SIZE>*>(net);
}

void MicroNAM_NanoNet_Reset(MicroNAM_NanoNet* net) {
    reinterpret_cast<NanoNet<NAM_BLOCK_SIZE>*>(net)->reset();
}

void MicroNAM_NanoNet_LoadWeights(MicroNAM_NanoNet* net, const float* weights) {
    reinterpret_cast<NanoNet<NAM_BLOCK_SIZE>*>(net)->load_weights(weights);
}

void MicroNAM_NanoNet_Process(MicroNAM_NanoNet* net, float* input, float* output) {
    reinterpret_cast<NanoNet<NAM_BLOCK_SIZE>*>(net)->forward(input, output);
}

// --- FeatherNet ---

MicroNAM_FeatherNet* MicroNAM_FeatherNet_Create(void) {
    return reinterpret_cast<MicroNAM_FeatherNet*>(new (std::nothrow) FeatherNet<NAM_BLOCK_SIZE>());
}

void MicroNAM_FeatherNet_Destroy(MicroNAM_FeatherNet* net) {
    delete reinterpret_cast<FeatherNet<NAM_BLOCK_SIZE>*>(net);
}

void MicroNAM_FeatherNet_Reset(MicroNAM_FeatherNet* net) {
    reinterpret_cast<FeatherNet<NAM_BLOCK_SIZE>*>(net)->reset();
}

void MicroNAM_FeatherNet_LoadWeights(MicroNAM_FeatherNet* net, const float* weights) {
    reinterpret_cast<FeatherNet<NAM_BLOCK_SIZE>*>(net)->load_weights(weights);
}

void MicroNAM_FeatherNet_Process(MicroNAM_FeatherNet* net, float* input, float* output) {
    reinterpret_cast<FeatherNet<NAM_BLOCK_SIZE>*>(net)->forward(input, output);
}

// --- LiteNet ---

MicroNAM_LiteNet* MicroNAM_LiteNet_Create(void) {
    return reinterpret_cast<MicroNAM_LiteNet*>(new (std::nothrow) LiteNet<NAM_BLOCK_SIZE>());
}

void MicroNAM_LiteNet_Destroy(MicroNAM_LiteNet* net) {
    delete reinterpret_cast<LiteNet<NAM_BLOCK_SIZE>*>(net);
}

void MicroNAM_LiteNet_Reset(MicroNAM_LiteNet* net) {
    reinterpret_cast<LiteNet<NAM_BLOCK_SIZE>*>(net)->reset();
}

void MicroNAM_LiteNet_LoadWeights(MicroNAM_LiteNet* net, const float* weights) {
    reinterpret_cast<LiteNet<NAM_BLOCK_SIZE>*>(net)->load_weights(weights);
}

void MicroNAM_LiteNet_Process(MicroNAM_LiteNet* net, float* input, float* output) {
    reinterpret_cast<LiteNet<NAM_BLOCK_SIZE>*>(net)->forward(input, output);
}

// --- StandardNet ---

MicroNAM_StandardNet* MicroNAM_StandardNet_Create(void) {
    return reinterpret_cast<MicroNAM_StandardNet*>(new (std::nothrow) StandardNet<NAM_BLOCK_SIZE>());
}

void MicroNAM_StandardNet_Destroy(MicroNAM_StandardNet* net) {
    delete reinterpret_cast<StandardNet<NAM_BLOCK_SIZE>*>(net);
}

void MicroNAM_StandardNet_Reset(MicroNAM_StandardNet* net) {
    reinterpret_cast<StandardNet<NAM_BLOCK_SIZE>*>(net)->reset();
}

void MicroNAM_StandardNet_LoadWeights(MicroNAM_StandardNet* net, const float* weights) {
    reinterpret_cast<StandardNet<NAM_BLOCK_SIZE>*>(net)->load_weights(weights);
}

void MicroNAM_StandardNet_Process(MicroNAM_StandardNet* net, float* input, float* output) {
    reinterpret_cast<StandardNet<NAM_BLOCK_SIZE>*>(net)->forward(input, output);
}

#ifdef __cplusplus
} // extern "C"
#endif
