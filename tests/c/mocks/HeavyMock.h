#ifndef _HEAVY_MOCK_H_
#define _HEAVY_MOCK_H_

#include "HvHeavyInternal.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct MockContext {
  hv_uint32_t currentSample;
  double sampleRate;
  // Add other state as needed for tests
} MockContext;

// Global mock context for convenience in tests
extern MockContext mockContext;

// Reset the mock context to default values
void mock_reset(void);

// Callback for messages sent from objects
typedef void (*MockSendCallback)(HeavyContextInterface *, int, const HvMessage *);
extern MockSendCallback lastSendCallback;
extern int lastSendLetIndex;
extern const HvMessage *lastSendMessage;

#ifdef __cplusplus
}
#endif

#endif
