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
  hv_size_t numBytes = msg_getCoreSize(1);
  o->list = (HvMessage *) hv_malloc(numBytes);
  hv_assert(o->list != NULL);
  msg_init(o->list, 1, 0);
  return numBytes;
}

void cList_free(ControlList *o) {
  hv_free(o->list);
}


HvMessage *cList_combine_lists(const HvMessage *a, const HvMessage *b) {
  int numElem1 = msg_getNumElements(a);
  int numElem2 = msg_getNumElements(b);
  int numElemTot = numElem1 + numElem2;

  hv_size_t numBytes = msg_getCoreSize(numElemTot);
  HvMessage *n = (HvMessage *) hv_malloc(numBytes);
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


static HvMessage *cList_trim(const HvMessage *m) {
  if (msg_isSymbol(m, 0)) {
    const char *s = msg_getSymbol(m, 0);
    if (!hv_strcmp(s, "list") || !hv_strcmp(s, "symbol")) {
      int numElements = msg_getNumElements(m);
      if (numElements <= 1) {
        HvMessage *n = (HvMessage *) hv_malloc(msg_getCoreSize(1));
        hv_assert(n != NULL);
        msg_initWithBang(n, msg_getTimestamp(m));
        return n;
      }
      hv_size_t numBytes = msg_getCoreSize(numElements-1);
      HvMessage *n = (HvMessage *) hv_malloc(numBytes);
      hv_assert(n != NULL);
      msg_init(n, numElements-1, msg_getTimestamp(m));

      for (int i = 1; i < numElements; i++) {
        switch(msg_getType(m, i)) {
          case HV_MSG_FLOAT: msg_setFloat(n, i-1, msg_getFloat(m, i)); break;
          case HV_MSG_SYMBOL: msg_setSymbol(n, i-1, msg_getSymbol(m, i)); break;
          default: break;
        }
      }

      return n;
    }
  }
  return (HvMessage *) m;
}


static HvMessage *cList_wrap_symbol(const HvMessage *m) {
  // Turns a bare symbol element into ["symbol", <sym>]
  // Only valid when msg_getNumElements(m) == 1 && msg_isSymbol(m, 0)
  HvMessage *n = (HvMessage *) hv_malloc(msg_getCoreSize(2));
  hv_assert(n != NULL);
  msg_init(n, 2, msg_getTimestamp(m));
  msg_setSymbol(n, 0, "symbol");
  msg_setSymbol(n, 1, msg_getSymbol(m, 0));
  return n;
}


static HvMessage *cList_slice(const HvMessage *m1, int start, int end) {
  if (start == end) {
    HvMessage *n = (HvMessage *) hv_malloc(msg_getCoreSize(1));
    hv_assert(n != NULL);
    msg_init(n, 1, msg_getTimestamp(m1));
    msg_setBang(n, 0);
    return n;
  }

  int sliceLen = end - start;
  bool firstIsSymbol = (msg_getType(m1, start) == HV_MSG_SYMBOL);
  int tag = firstIsSymbol ? 1 : 0;
  int allocLen = sliceLen + tag;

  HvMessage *n = (HvMessage *) hv_malloc(msg_getCoreSize(allocLen));
  hv_assert(n != NULL);
  msg_init(n, allocLen, msg_getTimestamp(m1));

  if (tag) {
    msg_setSymbol(n, 0, (sliceLen == 1) ? "symbol" : "list");
  }

  for (int i = start; i < end; i++) {
    switch (msg_getType(m1, i)) {
      case HV_MSG_FLOAT:  msg_setFloat(n,  i - start + tag, msg_getFloat(m1, i));  break;
      case HV_MSG_SYMBOL: msg_setSymbol(n, i - start + tag, msg_getSymbol(m1, i)); break;
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
          HvMessage *a = cList_trim(m);
          HvMessage *b = cList_trim(o->list);
          bool freeA = (a != m);
          bool freeB = (b != o->list);
          HvMessage *n = cList_combine_lists(a, b);
          sendMessage(_c, 0, n);
          hv_free(n);
          if (freeA) hv_free(a);
          if (freeB) hv_free(b);
          break;
        }
        case HV_LIST_PREPEND: {
          HvMessage *a = cList_trim(o->list);
          HvMessage *b = cList_trim(m);
          bool freeA = (a != o->list);
          bool freeB = (b != m);
          HvMessage *n = cList_combine_lists(a, b);
          sendMessage(_c, 0, n);
          hv_free(n);
          break;
        }
        case HV_LIST_SPLIT: {
          if (msg_isBang(m, 0)) {
            sendMessage(_c, 2, m);
            break;
          }

          HvMessage *m1 = cList_trim(m);
          bool trimmed = (m1 != m);
          int numElements = msg_getNumElements(m1);
          int split = (int) msg_getFloat(o->list, 0);

          if (split > numElements) {
            if (numElements == 1 && msg_getType(m1, 0) == HV_MSG_SYMBOL) {
              HvMessage *wrapped = cList_wrap_symbol(m1);
              sendMessage(_c, 2, wrapped);
              hv_free(wrapped);
            } else {
              sendMessage(_c, 2, m1);
            }
          } else if (split >= 0) {
            HvMessage *n1 = cList_slice(m1, 0, split);
            HvMessage *n2 = cList_slice(m1, split, numElements);
            sendMessage(_c, 1, n2);
            sendMessage(_c, 0, n1);
            hv_free(n1);
            hv_free(n2);
          }

          if (trimmed) hv_free(m1);
          break;
        }
        case HV_LIST_TRIM: {
          HvMessage *n = cList_trim(m);
          sendMessage(_c, 0, n);
          if (n != m) hv_free(n);
          break;
        }
        case HV_LIST_LENGTH: {
          HvMessage *n = HV_MESSAGE_ON_STACK(1);
          int numElements = msg_getNumElements(m);
          if (msg_isSymbol(m, 0)) {
            const char *s = msg_getSymbol(m, 0);
            if (!hv_strcmp(s, "list") || !hv_strcmp(s, "symbol")) {
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
      switch (o->type) {
        case HV_LIST_APPEND:
        case HV_LIST_PREPEND: {
          const int num = msg_getNumElements(m);
          HvMessage *tmp = HV_MESSAGE_ON_STACK(num);
          msg_init(tmp, num, 0);

          for (int i = 0; i < num; i++) {
            switch (msg_getType(m, i)) {
              case HV_MSG_FLOAT:  msg_setFloat(tmp, i, msg_getFloat(m, i));  break;
              case HV_MSG_SYMBOL: msg_setSymbol(tmp, i, msg_getSymbol(m, i)); break;
              default: break;
            }
          }
          msg_free(o->list);
          o->list = msg_copy(tmp);
          break;
        }
        case HV_LIST_SPLIT: {
          switch(msg_getType(m, 0)) {
            case HV_MSG_FLOAT: msg_setFloat(o->list, 0, msg_getFloat(m, 0)); break;
            case HV_MSG_SYMBOL: msg_setFloat(o->list, 0, 0); break;
            default: break;
          }
        }
        default: break;
      }
      break;
    }
    default: break;
  }
}
