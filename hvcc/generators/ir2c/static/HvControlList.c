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
  o->list = HV_MESSAGE_ON_HEAP(1);
  hv_assert(o->list != NULL);
  msg_initWithBang(o->list, 0);
  o->stride = 0;
  o->delim[0] = ' ';  // default delimiter is a space
  o->delim[1] = '\0'; // null-terminate the delimiter string
  return numBytes;
}

void cList_free(ControlList *o) {
  msg_free(o->list);
}

// ---- Utilities

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
   const int aIsEmpty = (msg_getNumElements(a) == 1 && msg_isBang(a, 0));
   const int bIsEmpty = (msg_getNumElements(b) == 1 && msg_isBang(b, 0));

   const int numElem1 = aIsEmpty ? 0 : msg_getNumElements(a);
   const int numElem2 = bIsEmpty ? 0 : msg_getNumElements(b);
   const int numElemTot = numElem1 + numElem2;

   // Always return a heap-allocated message so callers can unconditionally msg_free().
   HvMessage *n = HV_MESSAGE_ON_HEAP((numElemTot > 0) ? numElemTot : 1);
   hv_assert(n != NULL);

   if (numElemTot == 0) {
     msg_initWithBang(n, msg_getTimestamp(a));
     return n;
   }

   msg_init(n, numElemTot, msg_getTimestamp(a));
   int j = 0;
   if (!aIsEmpty) {
     for (int i = 0; i < numElem1; i++) cList_copy_message(a, i, n, j++);
   }
   if (!bIsEmpty) {
     for (int i = 0; i < numElem2; i++) cList_copy_message(b, i, n, j++);
   }
   return n;
}


static HvMessage *cList_trim(const HvMessage *m) {
  if (msg_isSymbol(m, 0)) {
    const char *s = msg_getSymbol(m, 0);
    if (!hv_strcmp(s, "list") || !hv_strcmp(s, "symbol")) {
      int numElements = msg_getNumElements(m);
      if (numElements <= 1) {
        HvMessage *n = HV_MESSAGE_ON_HEAP(1);
        hv_assert(n != NULL);
        msg_initWithBang(n, msg_getTimestamp(m));
        return n;
      }
      HvMessage *n = HV_MESSAGE_ON_HEAP(numElements - 1);
      hv_assert(n != NULL);
      msg_init(n, numElements - 1, msg_getTimestamp(m));

      for (int i = 1; i < numElements; i++) {
        cList_copy_message(m, i, n, i-1);
      }
      return n;
    }
  }
  return (HvMessage *) m;
}


static HvMessage *cList_wrap_symbol(const HvMessage *m) {
  // Turns a bare symbol element into ["symbol", <sym>]
  // Only valid when msg_getNumElements(m) == 1 && msg_isSymbol(m, 0)
  HvMessage *n = HV_MESSAGE_ON_HEAP(2);
  hv_assert(n != NULL);
  msg_init(n, 2, msg_getTimestamp(m));
  msg_setSymbol(n, 0, "symbol");
  msg_setSymbol(n, 1, msg_getSymbol(m, 0));
  return n;
}


static HvMessage *cList_untrim(const HvMessage *m) {
  if (msg_isSymbol(m, 0)) {
    int numElements = msg_getNumElements(m);
    if (numElements == 1) {
      return cList_wrap_symbol(m);
    }
    HvMessage *n = HV_MESSAGE_ON_HEAP(numElements + 1);
    hv_assert(n != NULL);
    msg_init(n, numElements + 1, msg_getTimestamp(m));

    msg_setSymbol(n, 0, "list");
    for (int i = 0; i < numElements; i++) {
      cList_copy_message(m, i, n, i + 1);
    }
    return n;
  }
  return (HvMessage *) m;
}


static HvMessage *cList_slice(const HvMessage *m1, int start, int end) {
  const int numElements = msg_getNumElements(m1);
  if (end < 0) end = numElements + 1 + end; // negative index

  if (start >= end || start < 0 || start >= numElements || end < 0 || end > numElements) {
    HvMessage *n = HV_MESSAGE_ON_HEAP(1);
    hv_assert(n != NULL);
    msg_init(n, 1, msg_getTimestamp(m1));
    msg_setBang(n, 0);
    return n;
  }

  int sliceLen = end - start;
  bool firstIsSymbol = (msg_getType(m1, start) == HV_MSG_SYMBOL);
  int tag = firstIsSymbol ? 1 : 0;
  int allocLen = sliceLen + tag;

  HvMessage *n = HV_MESSAGE_ON_HEAP(allocLen);
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


static size_t cList_put_delim(char *dst, const char *delim) {
  // Escapes a bare space with a backslash (an already-escaped "\ " is left alone).
  // With dst == NULL it only counts. Returns the number of bytes written/needed.
  size_t n = 0;
  for (size_t k = 0; delim[k] != '\0'; k++) {
    if (delim[k] == ' ' && (k == 0 || delim[k - 1] != '\\')) {
      if (dst) dst[n] = '\\';
      n++;
    }
    if (dst) dst[n] = delim[k];
    n++;
  }
  return n;
}


static size_t cList_join_build(const HvMessage *m, const char *delim, char *dst) {
  // Builds the joined string, trimming spaces at the outer edges of the list
  // only; interior element spaces are preserved. Pass dst == NULL to measure,
  // then call again with a buffer of (size + 1) bytes. Returns the length
  const int numElements = msg_getNumElements(m);
  size_t n = 0;
  bool first = true;

  for (int i = 0; i < numElements; i++) {
    const char *s = NULL;
    char numbuf[32];

    if (msg_isSymbol(m, i)) {
      s = msg_getSymbol(m, i);
      if (i == 0) {
        while (*s == ' ') s++;  // leading edge
      }
    } else if (msg_isFloat(m, i)) {
      hv_snprintf(numbuf, sizeof(numbuf), "%g", (double) msg_getFloat(m, i));
      s = numbuf;
    } else {
      continue;  // bang / hash carry no text
    }

    size_t len = strlen(s);
    if (i == numElements - 1) {
      while (len > 0 && s[len - 1] == ' ') len--;  // trailing edge
    }

    if (!first) n += cList_put_delim(dst ? dst + n : NULL, delim);
    first = false;

    if (dst) memcpy(dst + n, s, len);
    n += len;
  }

  if (dst) dst[n] = '\0';
  return n;
}


static size_t cList_match_delim(const char *s, const char *esc, size_t escLen,
    const char *raw, size_t rawLen) {
  // Bare-space delimiter, PD style: an escaped "\ " and a plain " " both split.
  if (rawLen == 1 && raw[0] == ' ') {
    if (s[0] == '\\' && s[1] == ' ') return 2;
    if (s[0] == ' ') return 1;
    return 0;
  }
  if (escLen > 0 && !strncmp(s, esc, escLen)) return escLen;
  if (rawLen > 0 && !strncmp(s, raw, rawLen)) return rawLen;
  return 0;
}


static bool cList_is_number(const char *s) {
  // True if the entire string is a valid number (the inverse of join's "%g").
  const size_t len = strlen(s);
  if (len == 0 || strspn(s, "0123456789+-.eE") != len) return false;
  char *end = NULL;
  strtod(s, &end);
  return end == s + len;
}


static void cList_set_token(HvMessage *n, int k, const char *tok) {
  // Stores a NUL-terminated token at index k: a float if the whole token is a
  // number, otherwise a symbol. The symbol pointer is stored, not copied, so tok
  // must outlive the message.
  if (cList_is_number(tok)) {
    msg_setFloat(n, k, (float) strtod(tok, NULL));
  } else {
    msg_setSymbol(n, k, tok);
  }
}


static char *cList_message_to_string(const HvMessage *m, bool symbolLike, size_t *outLen) {
  // Flattens m into one heap string. symbolLike: the message is one symbol, so
  // atoms are joined with an escaped space "\ " and any bare space inside an
  // atom is escaped too. Otherwise atoms are joined with a plain space.
  // Floats use "%g", bangs/hashes are skipped. Caller must hv_free() the result.
  const int numElements = msg_getNumElements(m);

  size_t total = 1;
  for (int i = 0; i < numElements; i++) {
    if (msg_isSymbol(m, i)) total += 2 * strlen(msg_getSymbol(m, i)) + 2;
    else if (msg_isFloat(m, i)) total += 34;
  }

  char *buf = (char *) hv_malloc(total);
  hv_assert(buf != NULL);

  size_t pos = 0;
  bool first = true;
  for (int i = 0; i < numElements; i++) {
    const char *s = NULL;
    char numbuf[32];
    if (msg_isSymbol(m, i)) {
      s = msg_getSymbol(m, i);
    } else if (msg_isFloat(m, i)) {
      hv_snprintf(numbuf, sizeof(numbuf), "%g", (double) msg_getFloat(m, i));
      s = numbuf;
    } else {
      continue;
    }

    if (!first) {
      if (symbolLike) buf[pos++] = '\\';
      buf[pos++] = ' ';
    }
    first = false;

    for (size_t k = 0; s[k] != '\0'; k++) {
      if (symbolLike && s[k] == ' ' && (k == 0 || s[k - 1] != '\\')) buf[pos++] = '\\';
      buf[pos++] = s[k];
    }
  }
  buf[pos] = '\0';
  *outLen = pos;
  return buf;
}

// ---- Message handlers

static void cList_onAppend(HeavyContextInterface *_c, ControlList *o, const HvMessage *m,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  HvMessage *a = cList_trim(m);
  const bool trimmed = (a != m);
  HvMessage *combined = cList_combine_lists(a, o->list);
  HvMessage *out = cList_untrim(combined);
  sendMessage(_c, 0, out);
  if (out != combined) msg_free(combined);
  msg_free(out);
  if (trimmed) msg_free(a);
}


static void cList_onPrepend(HeavyContextInterface *_c, ControlList *o, const HvMessage *m,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  HvMessage *b = cList_trim(m);
  const bool trimmed = (b != m);
  HvMessage *combined = cList_combine_lists(o->list, b);
  HvMessage *out = cList_untrim(combined);
  sendMessage(_c, 0, out);
  if (out != combined) msg_free(combined);
  msg_free(out);
  if (trimmed) msg_free(b);
}


static void cList_onSplit(HeavyContextInterface *_c, ControlList *o, const HvMessage *m, void
  (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
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
}


static void cList_onLength(HeavyContextInterface *_c, ControlList *o, const HvMessage *m, void
  (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  HvMessage *n = HV_MESSAGE_ON_HEAP(1);
  hv_assert(n != NULL);
  int numElements = msg_getNumElements(m);
  if (msg_isSymbol(m, 0)) {
    const char *s = msg_getSymbol(m, 0);
    if (!hv_strcmp(s, "list") || !hv_strcmp(s, "symbol")) {
      numElements -= 1;
    }
  }
  msg_initWithFloat(n, msg_getTimestamp(m), (float) numElements);
  sendMessage(_c, 0, n);
  msg_free(n);
}


static void cList_onForeach(HeavyContextInterface *_c, ControlList *o, const HvMessage *m, void
  (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  HvMessage *m1 = cList_trim(m);
  const bool trimmed = (m1 != m);
  const int numElements = msg_getNumElements(m1);

  // a stride of 0 is a chunk of 1; |stride| is clamped to the list length so
  // there is always at least one chunk and never an empty one
  int stride = o->stride;
  if (stride == 0) stride = 1;
  if (stride > numElements) stride = numElements;
  else if (stride < -numElements) stride = -numElements;

  const int step = (stride < 0) ? -stride : stride;
  const int numChunks = (numElements + step - 1) / step;

  for (int k = 0; k < numChunks; k++) {
    int start, end;
    if (stride > 0) {
      // forward: chunks cut from the head, so the short remainder is last
      start = k * step;
      end = hv_min_i(start + step, numElements);
    } else {
      // backward: the chunks are cut from the tail and emitted in reverse, so
      // the short remainder comes first and every piece keeps its element order
      start = numElements - (k + 1) * step;
      end = hv_min_i(start + step, numElements);
      if (start < 0) start = 0;
    }

    // the index of this chunk's first element goes out first, on outlet 1
    HvMessage *idx = HV_MESSAGE_ON_HEAP(1);
    hv_assert(idx != NULL);
    msg_initWithFloat(idx, msg_getTimestamp(m1), (float) start);
    sendMessage(_c, 1, idx);
    msg_free(idx);

    HvMessage *n = cList_slice(m1, start, end);
    sendMessage(_c, 0, n);
    msg_free(n);
  }

  if (trimmed) msg_free(m1);
}


static void cList_onJoin(HeavyContextInterface *_c, ControlList *o, const HvMessage *m, void
  (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  HvMessage *m1 = cList_trim(m);
  const bool trimmed = (m1 != m);

  const size_t size = cList_join_build(m1, o->delim, NULL);
  char *str = (char *) hv_malloc(size + 1);
  hv_assert(str != NULL);
  cList_join_build(m1, o->delim, str);

  HvMessage sym;
  msg_initWithSymbol(&sym, msg_getTimestamp(m1), str);

  // wrap as ["symbol", <str>] like the other outputs in this file
  HvMessage *out = cList_wrap_symbol(&sym);
  sendMessage(_c, 0, out);

  msg_free(out);
  hv_free(str);
  if (trimmed) msg_free(m1);
}


static void cList_onUnjoin(HeavyContextInterface *_c, ControlList *o, const HvMessage *m, void
  (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  // "symbol a\ b" may arrive as [symbol a b( or as one symbol; both are ONE symbol
  const bool tagged = msg_isSymbol(m, 0) && !hv_strcmp(msg_getSymbol(m, 0), "symbol");
  HvMessage *m1 = cList_trim(m);
  const bool trimmed = (m1 != m);
  const bool symbolLike = tagged || (msg_getNumElements(m1) == 1 && msg_isSymbol(m1, 0));

  size_t srcLen = 0;
  char *src = cList_message_to_string(m1, symbolLike, &srcLen);

  // Empty input, or an input that is entirely a number, yields a bang
  if (srcLen == 0 || cList_is_number(src)) {
    HvMessage *n = HV_MESSAGE_ON_HEAP(1);
    hv_assert(n != NULL);
    msg_initWithBang(n, msg_getTimestamp(m1));
    sendMessage(_c, 0, n);
    msg_free(n);
    hv_free(src);
    if (trimmed) msg_free(m1);
    return;
  }

  const char *delim = o->delim;
  const size_t rawLen = strlen(delim);

  char *chars = NULL;  // empty-delimiter case: one slot per character
  char *esc = NULL;
  HvMessage *n = NULL;

  if (rawLen == 0) {
    // Empty delimiter: one token per character.
    // An escaped space "\ " counts as ONE character.
    chars = (char *) hv_malloc(3 * srcLen + 1);
    hv_assert(chars != NULL);
    int numTokens = 0;
    size_t w = 0;
    for (size_t i = 0; i < srcLen; ) {
      if (src[i] == '\\' && src[i + 1] == ' ') {
        chars[w++] = '\\'; chars[w++] = ' '; chars[w++] = '\0';
        i += 2;
      } else {
        chars[w++] = src[i]; chars[w++] = '\0';
        i++;
      }
      numTokens++;
    }

    n = HV_MESSAGE_ON_HEAP(numTokens);
    hv_assert(n != NULL);
    msg_init(n, numTokens, msg_getTimestamp(m1));
    const char *tok = chars;
    for (int k = 0; k < numTokens; k++) {
      cList_set_token(n, k, tok);
      tok += strlen(tok) + 1;
    }
  } else {
    const size_t escLen = cList_put_delim(NULL, delim);
    esc = (char *) hv_malloc(escLen + 1);
    hv_assert(esc != NULL);
    cList_put_delim(esc, delim);
    esc[escLen] = '\0';

    int numTokens = 1;
    for (size_t i = 0; i < srcLen; ) {
      const size_t d = cList_match_delim(src + i, esc, escLen, delim, rawLen);
      if (d) { numTokens++; i += d; }
      else i++;
    }

    n = HV_MESSAGE_ON_HEAP(numTokens);
    hv_assert(n != NULL);
    msg_init(n, numTokens, msg_getTimestamp(m1));

    char *tok = src;
    int k = 0;
    size_t i = 0;
    for (;;) {
      const size_t d = (i < srcLen)
          ? cList_match_delim(src + i, esc, escLen, delim, rawLen) : 0;
      if (d == 0 && i < srcLen) { i++; continue; }

      src[i] = '\0';
      cList_set_token(n, k++, tok);
      if (i >= srcLen) break;
      i += d;
      tok = src + i;
    }
  }

  if (symbolLike) {
    // list/symbol tagging convention (untrim leaves a float-first result untagged)
    HvMessage *out = cList_untrim(n);
    sendMessage(_c, 0, out);
    if (out != n) msg_free(n);
    msg_free(out);
  } else {
    // true multi-atom output like [1 2 3 4(: no tag
    sendMessage(_c, 0, n);
    msg_free(n);
  }

  if (chars) hv_free(chars);
  if (esc) hv_free(esc);
  hv_free(src);
  if (trimmed) msg_free(m1);
}


// ---- Store handlers

static void cList_store_get(HeavyContextInterface *_c, ControlList *o, const HvMessage *m1, int numElements,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  const int index = (int) msg_getFloat(m1, 1);
  if (numElements >= 3) {
    const int length = (int) msg_getFloat(m1, 2);
    const int listLen = (int) msg_getNumElements(o->list);
    const int resolvedEnd = (length < 0) ? listLen : index + length;
    HvMessage *n = cList_slice(o->list, index, resolvedEnd);
    if (msg_isBang(n, 0)) {
      sendMessage(_c, 1, n);
    } else {
      sendMessage(_c, 0, n);
    }
    msg_free(n);
  } else {
    HvMessage *n = cList_slice(o->list, index, index + 1);
    if (msg_isBang(n, 0)) {
      sendMessage(_c, 1, n);
    } else {
      sendMessage(_c, 0, n);
    }
    msg_free(n);
  }
}


static void cList_store_set(ControlList *o, const HvMessage *m1, int numElements) {
  // Overwrite elements in o->list starting at index; superfluous payload items are ignored
  const int index = (int) msg_getFloat(m1, 1);
  const int listLen = msg_getNumElements(o->list);
  const int payloadLen = numElements - 2;
  const int count = (index + payloadLen > listLen) ? listLen - index : payloadLen;
  for (int i = 0; i < count; i++) {
    cList_copy_message(m1, 2 + i, o->list, index + i);
  }
}


static void cList_store_append(ControlList *o, const HvMessage *m1, int numElements) {
  // append our stored list
  HvMessage *a = o->list;
  HvMessage *slice = cList_slice(m1, 1, numElements);
  HvMessage *newList = cList_combine_lists(a, slice);
  msg_free(slice);
  msg_free(o->list);
  o->list = newList;
}


static void cList_store_prepend(ControlList *o, const HvMessage *m1, int numElements) {
  // prepend our stored list
  HvMessage *a = o->list;
  HvMessage *slice = cList_slice(m1, 1, numElements);
  HvMessage *newList = cList_combine_lists(slice, a);
  msg_free(slice);
  msg_free(o->list);
  o->list = newList;
}


static void cList_store_insert(ControlList *o, const HvMessage *m, const HvMessage *m1, int numElements) {
  // Split stored list at index, combine: head + payload + tail
  const int index = (int) msg_getFloat(m1, 1);
  const int listLen = msg_getNumElements(o->list);
  const int clampedIndex = (index < 0) ? 0 : (index > listLen) ? listLen : index;

  // payload is m1 elements [2, numElements) - copied raw, no list/symbol tag
  const int payloadLen = numElements - 2;
  if (payloadLen == 0) return;
  HvMessage *payload = HV_MESSAGE_ON_HEAP(payloadLen);
  hv_assert(payload != NULL);
  msg_init(payload, payloadLen, msg_getTimestamp(m));
  for (int i = 0; i < payloadLen; i++) {
    cList_copy_message(m1, 2 + i, payload, i);
  }
  HvMessage *head = (clampedIndex > 0)       ? cList_slice(o->list, 0, clampedIndex)       : NULL;
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
}


static void cList_store_delete(ControlList *o, const HvMessage *m, const HvMessage *m1, int numElements) {
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
    newList = HV_MESSAGE_ON_HEAP(1);
    hv_assert(newList != NULL);
    msg_initWithBang(newList, msg_getTimestamp(m));
  }

  msg_free(o->list);
  o->list = newList;
}


static void cList_store_send(HeavyContextInterface *_c, ControlList *o, const HvMessage *m1) {
  hv_uint32_t h = 0;
  switch (msg_getType(m1, 1)) {
    case HV_MSG_SYMBOL: h = hv_string_to_hash(msg_getSymbol(m1, 1)); break;
    case HV_MSG_HASH: h = msg_getHash(m1, 1); break;
    default: break;
  }
  HvMessage *n = cList_untrim(o->list);
  hv_sendMessageToReceiver(_c, h, 0, n);
  if (n != o->list) msg_free(n);
}


// ---- Main message handler entry point

void cList_onMessage(HeavyContextInterface *_c, ControlList *o, int letIn, const HvMessage *m,
  void (*sendMessage)(HeavyContextInterface *, int, const HvMessage *)) {
  switch (letIn) {
    case 0: {
      switch (o->type) {
        case HV_LIST_APPEND: {
          cList_onAppend(_c, o, m, sendMessage); break;
        }
        case HV_LIST_PREPEND: {
          cList_onPrepend(_c, o, m, sendMessage); break;
        }
        case HV_LIST_SPLIT: {
          if (msg_isBang(m, 0)) {
            sendMessage(_c, 2, m);
            break;
          }
          cList_onSplit(_c, o, m, sendMessage); break;
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
              cList_store_get(_c, o, m1, numElements, sendMessage);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "set")) {
              cList_store_set(o, m1, numElements);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "insert")) {
              cList_store_insert(o, m, m1, numElements);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "delete")) {
              cList_store_delete(o, m, m1, numElements);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "append")) {
              cList_store_append(o, m1, numElements);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "prepend")) {
              cList_store_prepend(o, m1, numElements);
              if (trimmed) msg_free(m1);
              break;
            } else if (!hv_strcmp(s, "send")) {
              if (numElements < 2) {
                // we technically should never get here
                if (trimmed) msg_free(m1);
                break;
              }
              cList_store_send(_c, o, m1);
              if (trimmed) msg_free(m1);
              break;
            } else {
              // No command matched - treat as data: prepend stored list
              HvMessage *n = cList_combine_lists(m1, o->list);
              HvMessage *out = cList_untrim(n);
              sendMessage(_c, 0, out);
              if (out != n) msg_free(out);
              if (trimmed) msg_free(m1);
              break;
            }
          }
          HvMessage *combined = cList_combine_lists(m1, o->list);
          HvMessage *n = cList_untrim(combined);
          sendMessage(_c, 0, n);
          if (n != combined) msg_free(combined);
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
          cList_onLength(_c, o, m, sendMessage); break;
        }
        case HV_LIST_FOREACH: {
          if (msg_isBang(m, 0)) break;
          cList_onForeach(_c, o, m, sendMessage); break;
        }
        case HV_LIST_JOIN: {
          if (msg_getNumElements(m) == 0 || msg_isBang(m, 0)) {
            HvMessage *n = HV_MESSAGE_ON_HEAP(1);
            msg_initWithSymbol(n, msg_getTimestamp(m), "symbol");
            sendMessage(_c, 0, n);
            msg_free(n);
            break;
          }
          cList_onJoin(_c, o, m, sendMessage); break;
        }
        case HV_LIST_UNJOIN: {
          if (msg_isBang(m, 0)) break;
          cList_onUnjoin(_c, o, m, sendMessage); break;
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
        case HV_LIST_FOREACH: {
          if (msg_isFloat(m, 0))
            o->stride = (int)msg_getFloat(m, 0);
          break;
        }
        case HV_LIST_JOIN:
        case HV_LIST_UNJOIN: {
          if (msg_isSymbol(m, 0)) {
            if (msg_getNumElements(m) > 1) {
              hv_strncpy(o->delim, msg_getSymbol(m, 1), HV_MAX_DELIM_LEN - 1);
              o->delim[HV_MAX_DELIM_LEN - 1] = '\0';
            } else {
              o->delim[0] = '\0';
            }
          }
          break;
        }
        default: break;
      }
      break;
    }
    default: break;
  }
}
