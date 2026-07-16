# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from collections import OrderedDict

from hvcc.core.hv2ir.HeavyGraph import HeavyGraph


def test_receiver_dict_sort():
    example_dict = {
        "[3]Bla": "something",
        "[2]Dong": "something",
        "nothing": "something",
        "[2]Ding": "something",
        "[11]Other": "something",
    }

    expected_dict = OrderedDict({
        "[2]Ding": "something",
        "[2]Dong": "something",
        "[3]Bla": "something",
        "[11]Other": "something",
        "nothing": "something",
    })

    ordered_dict = OrderedDict(sorted(example_dict.items(), key=HeavyGraph.sort_ir_receiver_dict))

    assert ordered_dict == expected_dict
