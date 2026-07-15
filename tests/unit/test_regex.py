# Heavy Compiler Collection
# Copyright (C) 2025-2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.core.hv2ir.HIrReceive import HIrReceive


def test_re_dollar():
    string = "12 $3 4 $56 7"
    result = PdParser.RE_DOLLAR.findall(string)

    assert result == ["3", "56"]


def test_re_width():
    string = "#X obj 172 79 t b b, f 22"
    result = PdParser.RE_WIDTH.sub("", string)

    assert result == "#X obj 172 79 t b b"


def test_re_space():
    string = r"some\ thing else"
    result = PdParser.RE_SPACE.split(string)

    assert result == ["some\\ thing", "else"]


def test_re_valid_recv():
    string1 = "some_name"
    string2 = "[1]somename"
    string3 = "[a]somename"
    string4 = "[1]"
    string5 = "[1][2]bla"
    string6 = ""

    assert HIrReceive.RE_VALID_RECV.match(string1) is not None
    assert HIrReceive.RE_VALID_RECV.match(string2) is not None
    assert HIrReceive.RE_VALID_RECV.match(string3) is None
    assert HIrReceive.RE_VALID_RECV.match(string4) is None
    assert HIrReceive.RE_VALID_RECV.match(string5) is None
    assert HIrReceive.RE_VALID_RECV.match(string6) is None
