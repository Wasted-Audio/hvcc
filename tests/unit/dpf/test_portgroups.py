import pytest

from hvcc.generators.c2dpf.c2dpf import _normalize_port_groups
from hvcc.types.meta import DPFPortGroupConfig, DPFPortGroups, slugify


def test_type():
    valid_groups = {
        "input": {"group1": {"one": 1, "two": (2, True)}},
        "output": {"group2": {"one": 1, "two": (2, False)}},
        "params": {"group3": ["param1", "param2"]}
    }

    duplicate_groups = {
        "input": {"group1": {"one": 1, "two": (1, True)}},
        "output": {"group1": {"one": 2, "two": (2, False)}},
    }

    duplicate_params = {
        "params": {
            "group1": ["param1", "param2"],
            "group2": ["param1"]
        }
    }

    duplicate_port_index = {
        "input": {"group1": {"one": 1, "two": (1, True)}},
    }

    duplicate_group_symbol: dict[str, dict[str, DPFPortGroupConfig]] = {
        "input": {"Group1": {"one": 1}, "group1": {"two": 2}},
    }

    DPFPortGroups(
        input=valid_groups["input"],
        output=valid_groups["output"],
        params=valid_groups["params"]
    )

    with pytest.raises(ValueError):
        DPFPortGroups(
            input=duplicate_groups["input"],
            output=duplicate_groups["output"]
        )

    with pytest.raises(ValueError):
        DPFPortGroups(
            params=duplicate_params["params"]
        )

    with pytest.raises(ValueError):
        DPFPortGroups(
            input=duplicate_port_index["input"]
        )

    with pytest.raises(ValueError):
        DPFPortGroups(
            input=duplicate_group_symbol["input"]
        )


def test_normalization():
    port_groups_valid = DPFPortGroups(
        input={"group1": {"one": 1, "two": 2}},
        output={"group2": {"one": 1, "two": 2}}
    )

    normalized_valid = _normalize_port_groups(port_groups_valid, num_input_channels=2, num_output_channels=2)
    assert normalized_valid is not None
    assert normalized_valid.input["group1"]["one"] == 0
    assert normalized_valid.output["group2"]["one"] == 0

    port_groups_invalid = DPFPortGroups(
        input={"group1": {"three": 3}},
    )

    with pytest.raises(ValueError):
        _normalize_port_groups(port_groups_invalid, num_input_channels=2, num_output_channels=2)


def test_slugify():
    assert slugify("Group 1") == "Group_1"
    assert slugify("group-2") == "group_2"
    assert slugify("GROUP 3") == "GROUP_3"
    assert slugify("Group-4") == "Group_4"
    assert slugify("Group 5-Test") == "Group_5_Test"
