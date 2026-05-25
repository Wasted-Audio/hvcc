from pathlib import Path
from textwrap import dedent

from hvcc.interpreters.pd2hv.PdParser import PdParser


def parse_subpatch(tmp_path: Path, array_lines: str):
    pd_path = tmp_path / "array_subpatch.pd"
    pd_path.write_text(
        "#N canvas 827 239 734 565 12;\n"
        "#N canvas 0 0 450 250 (subpatch) 0;\n"
        f"{dedent(array_lines)}"
        "#X coords 0 1 100 -1 200 140 1;\n"
        "#X restore 308 106 graph;\n"
    )

    graph = PdParser().graph_from_file(pd_path)
    assert not graph.get_notices().has_error
    return [obj for obj in graph.get_objects()[0].get_objects() if obj.obj_type == "table"]


def test_subpatch_parses_single_array(tmp_path: Path):
    tables = parse_subpatch(
        tmp_path,
        """\
        #X array array1 4 float 2;
        #A color 0;
        #A width 2;
        """,
    )

    assert [table.obj_dict["name"] for table in tables] == ["array1"]


def test_subpatch_parses_multiple_arrays(tmp_path: Path):
    tables = parse_subpatch(
        tmp_path,
        """\
        #X array array1 100 float 2;
        #A color 0;
        #A width 2;
        #X array array2 100 float 0;
        #A color 0;
        #A width 1;
        """,
    )

    assert [table.obj_dict["name"] for table in tables] == ["array1", "array2"]


def test_subpatch_parses_multi_line_arrays(tmp_path: Path):
    tables = parse_subpatch(
        tmp_path,
        """\
        #X array array1 4 float 2;
        #A 0 0 1;
        #A 2 2 3;
        #X array array2 4 float 0;
        #A 0 4 5;
        #A 2 6 7;
        """,
    )

    assert [table.obj_dict["name"] for table in tables] == ["array1", "array2"]
    assert [table.obj_dict["values"] for table in tables] == [
        [0.0, 1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0, 7.0],
    ]
