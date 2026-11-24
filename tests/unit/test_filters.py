import re

import pytest

from hvcc.generators import filters


def test_filter_max():
    assert filters.filter_max(1, 2) == 2
    assert filters.filter_max(5, 3) == 5
    assert filters.filter_max(-1, -4) == -1


def test_filter_max_accepts_strings():
    assert filters.filter_max("4", 2) == 4
    assert filters.filter_max(1, "7") == 7


@pytest.mark.parametrize("name", ["", "a", "patch", "some patch name", "sómething"])
def test_filter_plugin_id_range(name):
    plugin_id = filters.filter_plugin_id(name)
    assert 0 <= plugin_id <= 0x7FFF
    assert filters.filter_plugin_id(name) == plugin_id


def test_filter_string_cap_short():
    assert filters.filter_string_cap("abc", 10) == "abc"


def test_filter_string_cap_exact():
    assert filters.filter_string_cap("abc", 3) == "abc"


def test_filter_string_cap_truncated():
    result = filters.filter_string_cap("abcdefghij", 8)
    assert result == "abcde..."
    assert len(result) == 8


def test_filter_templates():
    assert filters.filter_templates("/some/path/.DS_Store") is False
    assert filters.filter_templates(".DS_Store") is False
    assert filters.filter_templates("/some/path/template.c") is True
    assert filters.filter_templates("template.c") is True


def test_filter_uniqueid_format():
    uniqueid = filters.filter_uniqueid("patch")
    assert re.fullmatch(r"0x[0-9A-F]{8}", uniqueid)
    assert filters.filter_uniqueid("patch") == uniqueid


@pytest.mark.parametrize(
    "filter",
    [filters.filter_xcode_build, filters.filter_xcode_copy, filters.filter_xcode_fileref]
)
def test_filter_xcode_hashes_are_24_upper_hex(filter):
    h = filter("SomeName")
    assert re.fullmatch(r"[0-9A-F]{24}", h)
    assert filter("SomeName") == h


def test_filter_xcode_hashes_differ_per_purpose():
    name = "SomeName"
    hashes = {
        filters.filter_xcode_build(name),
        filters.filter_xcode_copy(name),
        filters.filter_xcode_fileref(name),
    }
    assert len(hashes) == 3
