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
  msg_initWithBang(o->list, 1);
  return numBytes;
}

void cList_free(ControlList *o) {
  msg_free(o->list);
}

void cList_copy_message(const HvMessage *m, int i, HvMessage *tmp, int j) {
  switch (msg_getType(m, i)) {
    case HV_MSG_FLOAT: msg_setFloat(tmp, j, msg_getFloat(m, i)); break;
    case HV_MSG_SYMBOL: msg_setSymbol(tmp, j, msg_getSymbol(m, i)); break;
    case HV_MSG_BANG: msg_setBang(tmp, j); break;
    case HV_MSG_HASH: msg_setHash(tmp, j, msg_getHash(m, i)); break;
    default: break;
  }
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
    cList_copy_message(a, i, n, i);
  }

  for (int i = 0; i < numElem2; i++) {
    cList_copy_message(b, i, n, numElem1 + i);
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
        cList_copy_message(m, i, n, i-1);
      }

      return n;
    }
  }
  return (HvMessage *) m;
}


static HvMessage *cList_untrim(const HvMessage *m) {
  if (msg_isSymbol(m, 0)) {
    int numElements = msg_getNumElements(m);
    if (numElements <= 1) {
      return (HvMessage *) m;
    }
    hv_size_t numBytes = msg_getCoreSize(numElements+1);
    HvMessage *n = (HvMessage *) hv_malloc(numBytes);
    hv_assert(n != NULL);
    msg_init(n, numElements+1, msg_getTimestamp(m));

    msg_setSymbol(n, 0, "list");
    for (int i = 0; i < numElements; i++) {
      cList_copy_message(m, i, n, i+1);
    }

    return n;
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
  const int numElements = msg_getNumElements(m1);
  if (end < 0) end = numElements + 1 + end; // negative index

  if (start >= end || start < 0 || start >= numElements || end < 0 || end > numElements) {
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
    cList_copy_message(m1, i, n, i - start + tag);
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
          HvMessage *b = o->list;
          bool freeA = (a != m);
          bool freeB = (b != o->list);
          HvMessage *n = cList_combine_lists(a, b);
          sendMessage(_c, 0, n);
          msg_free(n);
          if (freeA) msg_free(a);
          if (freeB) msg_free(b);
          break;
        }
        case HV_LIST_PREPEND: {
          HvMessage *a = o->list;
          HvMessage *b = cList_trim(m);
          bool freeA = (a != o->list);
          bool freeB = (b != m);
          HvMessage *n = cList_combine_lists(a, b);
          sendMessage(_c, 0, n);
          msg_free(n);
          if (freeA) msg_free(a);
          if (freeB) msg_free(b);
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
              msg_free(wrapped);
            } else {
              sendMessage(_c, 2, m1);
            }
          } else if (split >= 0) {
            HvMessage *n1 = cList_slice(m1, 0, split);
            HvMessage *n2 = cList_slice(m1, split, numElements);
            sendMessage(_c, 1, n2);
            sendMessage(_c, 0, n1);
            msg_free(n1);
            msg_free(n2);
          }

          if (trimmed) msg_free(m1);
          break;
        }
        case HV_LIST_STORE: {
          // just output the stored list
          if (msg_isBang(m, 0)) {
            HvMessage *n = cList_untrim(o->list);
            sendMessage(_c, 0, n);
            if (n != o->list) msg_free(n);
            break;
          }

          HvMessage *m1 = cList_trim(m); // trim before any checks
          bool trimmed = (m1 != m);
          int numElements = msg_getNumElements(m1);

          if (msg_isSymbol(m1, 0)) {
            const char *s = msg_getSymbol(m1, 0);
            if (!hv_strcmp(s, "get")) {
              const int index = (int) msg_getFloat(m1, 1);
              if (numElements >= 3) {
                int end = (int) msg_getFloat(m1, 2);
                if (trimmed) msg_free(m1);
                // detrimine correct end index
                const int resolvedEnd = (end < 0) ? msg_getNumElements(o->list) + 1 | end : end + 1;
                HvMessage *n = cList_slice(o->list, index, resolvedEnd);
                if (msg_isBang(n, 0)) {
                  sendMessage(_c, 1, n);
                  msg_free(n);
                  break;
                }
                sendMessage(_c, 0, n);
                msg_free(n);
                break;
              } else {
                HvMessage *n = cList_slice(o->list, index, index + 1);
                sendMessage(_c, 0, n);
                msg_free(n);
                if (trimmed) msg_free(m1);
                break;
              }
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "set")) {
              // Overwrite elements in o->list starting at index; superfluous payload items are ignored
              const int index = (int) msg_getFloat(m1, 1);
              const int listLen = msg_getNumElements(o->list);
              const int payloadLen = numElements - 2;
              const int count = (index + payloadLen > listLen) ? listLen - index : payloadLen;
              for (int i = 0; i < count; i++) {
                cList_copy_message(m1, 2 + i, o->list, index + i);
              }
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "insert")) {
              // Split stored list at index, combine: head + payload + tail
              const int index = (int) msg_getFloat(m1, 1);
              const int listLen = msg_getNumElements(o->list);
              const int clampedIndex = (index < 0) ? 0 : (index > listLen) ? listLen : index;

              // payload is m1 elements [2, numElements) - copied raw, no list/symbol tag
              const int payloadLen = numElements - 2;
              HvMessage *payload = (HvMessage *) hv_malloc(msg_getCoreSize(payloadLen));
              hv_assert(payload != NULL);
              msg_init(payload, payloadLen, msg_getTimestamp(m));
              for (int i = 0; i < payloadLen; i++) {
                cList_copy_message(m1, 2 + i, payload, i);
              }
              HvMessage *head = (clampedIndex > 0)       ? cList_slice(o->list, 0, clampedIndex)           : NULL;
              HvMessage *tail = (clampedIndex < listLen) ? cList_slice(o->list, clampedIndex, listLen) : NULL;

              HvMessage *newList;
              if (head && tail) {
                HvMessage *tmp = cList_combine_lists(head, payload);
                newList = cList_combine_lists(tmp, tail);
                msg_free(tmp);
                msg_free(head);
                msg_free(tail);
              } else if (head) {
                newList = cList_combine_lists(head, payload);
                msg_free(head);
              } else if (tail) {
                newList = cList_combine_lists(payload, tail);
                msg_free(tail);
              } else {
                // list was empty, payload becomes the list
                newList = payload;
                payload = NULL; // transferred ownership, skip free below
              }

              if (payload) msg_free(payload);
              msg_free(o->list);
              o->list = newList;
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "delete")) {
              const int index = (int) msg_getFloat(m1, 1);
              const int listLen = msg_getNumElements(o->list);
              int end;
              if (numElements >= 3) {
                int count = (int) msg_getFloat(m1, 2);
                end = (count < 0) ? listLen : index + count;
              } else {
                end = index + 1;
              }
              if (end > listLen) end = listLen;

              // Build new list from [0, index) + [end, listLen)
              HvMessage *head = (index > 0)    ? cList_slice(o->list, 0, index)      : NULL;
              HvMessage *tail = (end < listLen) ? cList_slice(o->list, end, listLen) : NULL;

              HvMessage *newList;
              if (head && tail) {
                newList = cList_combine_lists(head, tail);
                msg_free(head);
                msg_free(tail);
              } else if (head) {
                newList = head;
              } else if (tail) {
                newList = tail;
              } else {
                // deleted everything - store an empty bang
                newList = (HvMessage *) hv_malloc(msg_getCoreSize(1));
                hv_assert(newList != NULL);
                msg_initWithBang(newList, msg_getTimestamp(m));
              }

              msg_free(o->list);
              o->list = newList;
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "append")) {
              HvMessage *a = o->list;
              HvMessage *slice = cList_slice(m1, 1, numElements);
              HvMessage *newList = cList_combine_lists(slice, a);
              msg_free(slice);
              msg_free(o->list);
              o->list = newList;
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "prepend")) {
              HvMessage *a = o->list;
              HvMessage *slice = cList_slice(m1, 1, numElements);
              HvMessage *newList = cList_combine_lists(a, slice);
              msg_free(slice);
              msg_free(o->list);
              o->list = newList;
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "send")) {
              hv_uint32_t h = 0;
              switch (msg_getType(m1, 1)) {
                case HV_MSG_SYMBOL:
                  h = hv_string_to_hash(msg_getSymbol(m1, 1));
                  if (trimmed) msg_free(m1);
                  break;
                case HV_MSG_HASH:
                  h = msg_getHash(m1, 1);
                  if (trimmed) msg_free(m1);
                  break;
                case HV_MSG_FLOAT:
                case HV_MSG_BANG:
                  break;
              }
              HvMessage *n = cList_untrim(o->list);
              hv_sendMessageToReceiver(_c, h, 0, n);
              if (n != o->list) msg_free(n);
              break;
            } else {
              // No command matched - treat as data: prepend stored list
              HvMessage *n = cList_combine_lists(m1, o->list);
              HvMessage *out = cList_untrim(n);
              sendMessage(_c, 0, out);
              msg_free(n);
              if (out != n) msg_free(out);
              if (trimmed) msg_free(m1);
              break;
            }
            break;
          }
          HvMessage *b = o->list;
          HvMessage *n = cList_untrim(cList_combine_lists(m1, b));
          sendMessage(_c, 0, n);
          msg_free(n);
          if (trimmed) msg_free(m1);
          break;
        }
        case HV_LIST_TRIM: {
          HvMessage *n = cList_trim(m);
          sendMessage(_c, 0, n);
          if (n != m) msg_free(n);
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
        case HV_LIST_PREPEND:
        case HV_LIST_STORE: {
          HvMessage *n = cList_trim(m);
          HvMessage *newList = msg_copy(n);
          if (n != m) msg_free(n);
          msg_free(o->list);
          o->list = newList;
          break;
        }
        case HV_LIST_SPLIT: {
          cList_copy_message(m, 0, o->list, 0);
          break;
        }
        default: break;
      }
      break;
    }
    default: break;
  }
}
