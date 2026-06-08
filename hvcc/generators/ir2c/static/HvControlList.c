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

#include "HvControlList.h"

hv_size_t cList_init(ControlList *o, hvListType type) {
  o->type = type;
  hv_size_t numBytes = msg_getCoreSize(32);
  o->list = (HvMessage *) hv_malloc(numBytes);
  hv_assert(o->list != NULL);
  msg_init(o->list, 32, 0);
  return numBytes;
}

void cList_free(ControlList *o) {
  hv_free(o->list);
}


HvMessage* cList_combine_lists(const HvMessage *a, const HvMessage *b) {
  int numElem1 = msg_getNumElements(a);
  int numElem2 = msg_getNumElements(b);
  int numElemTot = numElem1 + numElem2;

  hv_size_t numBytes = msg_getCoreSize(numElemTot);
  HvMessage* n = (HvMessage *) hv_malloc(numBytes);
  hv_assert(n != NULL);
  msg_init(n, numElemTot, msg_getTimestamp(a));

  for (int i = 0; i < numElem1; i++) {
    switch(msg_getType(a, i)) {
      case HV_MSG_FLOAT: msg_setFloat(n, i, msg_getFloat(a, i)); break;
      case HV_MSG_SYMBOL: msg_setSymbol(n, i, msg_getSymbol(a, i)); break;
      default: break;
    }
  }

  for (int i = 0; i < numElem2; i++) {
    switch(msg_getType(b, i)) {
      case HV_MSG_FLOAT: msg_setFloat(n, numElem1 + i, msg_getFloat(b, i)); break;
      case HV_MSG_SYMBOL: msg_setSymbol(n, numElem1 + i, msg_getSymbol(b, i)); break;
      default: break;
    }
  }

  return n;
}


void cList_onMessage(HeavyContextInterface *_c, ControlList *o, int letIn, const HvMessage *m,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {

  switch (letIn) {
    case 0: {
      switch (o->type) {
        case HV_LIST_APPEND: {
          HvMessage *n = cList_combine_lists(m, o->list);
          sendMessage(_c, 0, n);
          break;
        }
        case HV_LIST_PREPEND: {
          HvMessage *n = cList_combine_lists(o->list, m);
          sendMessage(_c, 0, n);
          break;
        }
        case HV_LIST_TRIM: {
          int numElements = msg_getNumElements(m);
          if (msg_isSymbol(m, 0)) {
            if (!hv_strcmp(msg_getSymbol(m, 0), "list")) {
              hv_size_t numBytes = msg_getCoreSize(numElements-1);
              HvMessage* n = (HvMessage *) hv_malloc(numBytes);
              hv_assert(n != NULL);
              msg_init(n, numElements-1, msg_getTimestamp(m));

              for (int i = 1; i < numElements; i++) {
                switch(msg_getType(m, i)) {
                  case HV_MSG_FLOAT: msg_setFloat(n, i-1, msg_getFloat(m, i)); break;
                  case HV_MSG_SYMBOL: msg_setSymbol(n, i-1, msg_getSymbol(m, i)); break;
                  default: break;
                }
              }
              sendMessage(_c, 0, n);
              break;
            }
          }
          sendMessage(_c, 0, m);
          break;
        }
        case HV_LIST_LENGTH: {
          HvMessage *n = HV_MESSAGE_ON_STACK(1);
          int numElements = msg_getNumElements(m);
          if (msg_isSymbol(m, 0)) {
            if (!hv_strcmp(msg_getSymbol(m, 0), "list")) {
              numElements -= 1;
            }
          }
          msg_initWithFloat(n, msg_getTimestamp(m), numElements);
          sendMessage(_c, 0, n);
          break;
        }
        default: break;
      }
      break;
    }
    case 1: {
      const int numElements = msg_getNumElements(m);
      o->list->numElements = numElements;
      for (int i = 0; i < numElements; i++) {
        switch(msg_getType(m, i)) {
          case HV_MSG_FLOAT:
            msg_setFloat(o->list, i, msg_getFloat(m, i)); break;
          case HV_MSG_SYMBOL:
            msg_setSymbol(o->list, i, msg_getSymbol(m, i)); break;
          default: break;
        }
      }
      break;
    }
    default: {
      break;
    }
  }
}
