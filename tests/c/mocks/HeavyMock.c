#include "HeavyMock.h"
#include "HvMessage.h"
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

MockContext mockContext;
MockSendCallback lastSendCallback = NULL;
int lastSendLetIndex = -1;
const HvMessage *lastSendMessage = NULL;

void mock_reset(void) {
  memset(&mockContext, 0, sizeof(MockContext));
  mockContext.sampleRate = 44100.0;
  lastSendCallback = NULL;
  lastSendLetIndex = -1;
  lastSendMessage = NULL;
}

// Context accessors
hv_uint32_t hv_getCurrentSample(HeavyContextInterface *c) {
  return mockContext.currentSample;
}

double hv_getSampleRate(HeavyContextInterface *c) {
  return mockContext.sampleRate;
}

// Message scheduling
HvMessage *hv_scheduleMessageForObject(HeavyContextInterface *c, const HvMessage *m,
    void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *),
    int letIndex) {
  lastSendCallback = sendMessage;
  lastSendLetIndex = letIndex;
  lastSendMessage = m;
  return (HvMessage *)m; 
}

void hv_scheduleMessageForReceiver(HeavyContextInterface *c, hv_uint32_t receiverHash, HvMessage *m) { }

// Table access
float *hv_table_getBuffer(HeavyContextInterface *c, hv_uint32_t tableHash) { return NULL; }
hv_uint32_t hv_table_getLength(HeavyContextInterface *c, hv_uint32_t tableHash) { return 0; }

// Utils
hv_uint32_t hv_string_to_hash(const char *s) {
  if (s == NULL) return 0;
  hv_uint32_t hash = 0;
  while (*s) {
    hash = hash * 31 + *s++;
  }
  return hash;
}

void hv_assert_fail(const char *expr, const char *file, int line) {
    fprintf(stderr, "Assertion failed: %s at %s:%d\n", expr, file, line);
    exit(1);
}

// Message implementations
HvMessage *msg_init(HvMessage *m, hv_size_t numElements, hv_uint32_t timestamp) {
  m->timestamp = timestamp;
  m->numElements = (hv_uint16_t) numElements;
  m->numBytes = (hv_uint16_t) msg_getCoreSize(numElements);
  return m;
}

HvMessage *msg_initWithFloat(HvMessage *m, hv_uint32_t timestamp, float f) {
  msg_init(m, 1, timestamp);
  msg_setFloat(m, 0, f);
  return m;
}

HvMessage *msg_initWithBang(HvMessage *m, hv_uint32_t timestamp) {
  msg_init(m, 1, timestamp);
  msg_setBang(m, 0);
  return m;
}

HvMessage *msg_initWithSymbol(HvMessage *m, hv_uint32_t timestamp, const char *s) {
  msg_init(m, 1, timestamp);
  msg_setSymbol(m, 0, s);
  return m;
}

HvMessage *msg_initWithHash(HvMessage *m, hv_uint32_t timestamp, hv_uint32_t h) {
  msg_init(m, 1, timestamp);
  msg_setHash(m, 0, h);
  return m;
}

void msg_free(HvMessage *m) { }

HvMessage *msg_copy(const HvMessage *m) {
    hv_size_t size = msg_getCoreSize(m->numElements);
    HvMessage *n = (HvMessage *) malloc(size);
    memcpy(n, m, size);
    return n;
}
