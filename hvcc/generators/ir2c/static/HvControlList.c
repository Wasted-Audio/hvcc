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

hv_size_t cList_init(ControlList *o, hvListType type, int size) {
  o->type = type;
  hv_size_t numBytes = msg_getCoreSize(size);
  o->list = (HvMessage *) hv_malloc(numBytes);
  hv_assert(o->list != NULL);
  msg_init(o->list, size, 0);
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


HvMessage* cList_trim(const HvMessage *m) {
  int numElements = msg_getNumElements(m);
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
        case HV_LIST_SPLIT: {
          HvMessage *m1 = (HvMessage *) m;
          if (msg_isSymbol(m, 0)) {
            if (!hv_strcmp(msg_getSymbol(m, 0), "list") || !hv_strcmp(msg_getSymbol(m, 0), "symbol")) {
             m1 = cList_trim(m);
            }
          }

          int numElements = msg_getNumElements(m1);
          int split = (int) msg_getFloat(o->list, 0);

          if (split >= 0 && split <= numElements) {

            int off1 = 0;
            if (msg_getType(m, 0) == HV_MSG_SYMBOL) {
              off1 = 1;
            }

            HvMessage* n1 = (HvMessage *) hv_malloc(msg_getCoreSize(split+off1));
            hv_assert(n1 != NULL);
            msg_init(n1, split+off1, msg_getTimestamp(m1));

            if (off1 == 1) {
              if (split > 1) {
                msg_setSymbol(n1, 0, "list");
              } else {
                msg_setSymbol(n1, 0, "symbol");
              }
            }

            for (int i = 0; i < split; i++) {
              switch(msg_getType(m1, i)) {
                case HV_MSG_FLOAT: msg_setFloat(n1, i+off1, msg_getFloat(m1, i)); break;
                case HV_MSG_SYMBOL: msg_setSymbol(n1, i+off1, msg_getSymbol(m1, i)); break;
                default: break;
              }
            }

            HvMessage* n2;

            if (split < numElements) {
              int off2 = 0;
              if (msg_getType(m, split) == HV_MSG_SYMBOL) {
                off2 = 1;
              }

              n2 = (HvMessage *) hv_malloc(msg_getCoreSize(numElements-split+off2));
              hv_assert(n2 != NULL);
              msg_init(n2, numElements-split+off2, msg_getTimestamp(m1));

              if (numElements - split != 0) {
                if (off2 == 1) {
                  if (numElements-split > 1) {
                    msg_setSymbol(n2, 0, "list");
                  } else {
                    msg_setSymbol(n2, 0, "symbol");
                  }
                }

                for (int i = split; i < numElements; i++) {
                  switch(msg_getType(m1, i)) {
                    case HV_MSG_FLOAT: msg_setFloat(n2, i-split+off2, msg_getFloat(m1, i)); break;
                    case HV_MSG_SYMBOL: msg_setSymbol(n2, i-split+off2, msg_getSymbol(m1, i)); break;
                    default: break;
                  }
                }
              }
            } else if (split == numElements) {
              n2 = (HvMessage *) hv_malloc(msg_getCoreSize(1));
              hv_assert(n2 != NULL);
              msg_init(n2, 1, msg_getTimestamp(m1));
              msg_setBang(n2, 0);
            }

            sendMessage(_c, 1, n2);
            sendMessage(_c, 0, n1);
            break;
          } else if (split > numElements) {
            if (numElements == 1 && msg_getType(m1, 0) == HV_MSG_SYMBOL) {
              m1->numElements = 2;
              msg_setSymbol(m1, 1, msg_getSymbol(m1, 0));
              msg_setSymbol(m1, 0, "symbol");
            }
            sendMessage(_c, 2, m1);
            break;
          }
          break;
        }
        case HV_LIST_TRIM: {
          if (msg_isSymbol(m, 0)) {
            if (!hv_strcmp(msg_getSymbol(m, 0), "list")) {
              HvMessage *n = cList_trim(m);
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
      switch (o->type) {
        case HV_LIST_APPEND:
        case HV_LIST_PREPEND: {
          const int numElements = msg_getNumElements(m);
          o->list->numElements = numElements;
          for (int i = 0; i < numElements; i++) {
            switch(msg_getType(m, i)) {
              case HV_MSG_FLOAT: msg_setFloat(o->list, i, msg_getFloat(m, i)); break;
              case HV_MSG_SYMBOL: msg_setSymbol(o->list, i, msg_getSymbol(m, i)); break;
              default: break;
            }
          }
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
    }
    default: break;
  }
}
