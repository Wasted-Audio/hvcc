from pathlib import Path

from hvcc.interpreters.pd2hv.PdGraph import PdGraph
from hvcc.interpreters.pd2hv.PdParser import PdParser


def test_single_array_in_subpatch(tmp_path: Path):
    pd_path = tmp_path / "single_array_subpatch.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#N canvas 0 0 450 250 (subpatch) 0;
#X array array1 4 float 2;
#A color 0;
#A width 2;
#X coords 0 1 100 -1 200 140 1;
#X restore 308 106 graph;
"""
    )

    graph = PdParser().graph_from_file(pd_path)

    assert not graph.get_notices().has_error

    subpatch = graph.get_objects()[0]
    tables = [obj for obj in subpatch.get_objects() if obj.obj_type == "table"]

    assert [table.obj_dict["name"] for table in tables] == ["array1"]


def test_multiple_arrays_in_subpatch(tmp_path: Path):
    pd_path = tmp_path / "multi_array_subpatch.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#N canvas 0 0 450 250 (subpatch) 0;
#X array array1 100 float 2;
#A color 0;
#A width 2;
#X array array2 100 float 0;
#A color 0;
#A width 1;
#X coords 0 1 100 -1 200 140 1;
#X restore 308 106 graph;
"""
    )

    graph = PdParser().graph_from_file(pd_path)

    assert not graph.get_notices().has_error

    subpatch = graph.get_objects()[0]
    tables = [obj for obj in subpatch.get_objects() if obj.obj_type == "table"]

    assert [table.obj_dict["name"] for table in tables] == ["array1", "array2"]


def test_multi_line_arrays(tmp_path: Path):
    pd_path = tmp_path / "multiline_arrays_subpatch.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#N canvas 0 0 450 250 (subpatch) 0;
#X array array1 4 float 2;
#A 0 0 1;
#A 2 2 3;
#A color 0;
#A width 2;
#X array array2 4 float 0;
#A 0 4 5;
#A 2 6 7;
#A color 0;
#A width 1;
#X coords 0 1 100 -1 200 140 1;
#X restore 308 106 graph;
"""
    )

    graph = PdParser().graph_from_file(pd_path)

    assert not graph.get_notices().has_error

    subpatch = graph.get_objects()[0]
    tables = [obj for obj in subpatch.get_objects() if obj.obj_type == "table"]

    assert [table.obj_dict["name"] for table in tables] == ["array1", "array2"]
    assert [table.obj_dict["values"] for table in tables] == [
        [0.0, 1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0, 7.0],
    ]


def test_nam_path(tmp_path: Path):
    pd_path = tmp_path / "nam_path.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 86 129 pdnam~ test.nam;
""")

    graph = PdParser().graph_from_file(pd_path)
    assert not graph.get_notices().has_error

    nam_object = graph.get_objects()[0].get_objects()[1]
    assert Path(nam_object.obj_dict["nam"]) == tmp_path / "test.nam"


def test_block_size_propagation(tmp_path: Path):
    pd_path = tmp_path / "test_block_size.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 50 50 block~ 1024;
#N canvas 0 0 450 250 subpatch 0;
#X obj 100 100 osc~ 440;
#X restore 308 106 pd subpatch;
#N canvas 0 0 450 250 subpatch_override 0;
#X obj 50 50 block~ 256;
#X obj 100 100 osc~ 440;
#X restore 308 206 pd subpatch_override;
"""
    )

    graph = PdParser().graph_from_file(pd_path)
    assert graph.block_size == 1024

    subpatch = next(o for o in graph.get_objects() if getattr(o, "subpatch_name", None) == "subpatch")
    assert subpatch.block_size == 1024
    assert subpatch.to_hv().block_size == 1024

    override = next(o for o in graph.get_objects() if getattr(o, "subpatch_name", None) == "subpatch_override")
    assert override.block_size == 256
    assert override.to_hv().block_size == 256


def test_block_size_propagation_order_independent(tmp_path: Path):
    pd_path = tmp_path / "test_block_size_after.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#N canvas 0 0 450 250 subpatch 0;
#X obj 100 100 osc~ 440;
#X restore 308 106 pd subpatch;
#X obj 50 50 block~ 512;
"""
    )

    graph = PdParser().graph_from_file(pd_path)
    assert graph.block_size == 512

    subpatch = next(o for o in graph.get_objects() if getattr(o, "subpatch_name", None) == "subpatch")
    assert subpatch.block_size == 512
    assert subpatch.to_hv().block_size == 512


def test_block_size_propagation_nested_subpatches(tmp_path: Path):
    pd_path = tmp_path / "test_block_size_nested.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 50 50 block~ 1024;
#N canvas 0 0 450 250 parent_sub 0;
#N canvas 0 0 450 250 child_sub 0;
#X obj 100 100 osc~ 440;
#X restore 100 100 pd child_sub;
#X restore 308 106 pd parent_sub;
"""
    )

    graph = PdParser().graph_from_file(pd_path)
    assert graph.block_size == 1024

    parent_sub = next(o for o in graph.get_objects() if getattr(o, "subpatch_name", None) == "parent_sub")
    assert parent_sub.block_size == 1024
    assert parent_sub.to_hv().block_size == 1024

    child_sub = next(o for o in parent_sub.get_objects() if getattr(o, "subpatch_name", None) == "child_sub")
    assert child_sub.block_size == 1024
    assert child_sub.to_hv().block_size == 1024


def test_block_size_propagation_abstraction(tmp_path: Path):
    abs_path = tmp_path / "my_abs.pd"
    abs_path.write_text(
        """#N canvas 0 0 450 250 12;
#X obj 100 100 osc~ 440;
"""
    )
    main_path = tmp_path / "main.pd"
    main_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 50 50 block~ 1024;
#X obj 100 100 my_abs;
"""
    )

    parser = PdParser()
    parser.add_absolute_search_directory(tmp_path)
    graph = parser.graph_from_file(main_path)
    assert graph.block_size == 1024

    abs_obj = next(o for o in graph.get_objects() if isinstance(o, PdGraph))
    assert abs_obj.block_size == 1024
    assert abs_obj.to_hv().block_size == 1024


def test_block_size_propagation_pdlib_in_subpatch(tmp_path: Path):
    pd_path = tmp_path / "test_pdlib_sub.pd"
    pd_path.write_text(
        """#N canvas 1039 0 450 300 12;
#N canvas 1216 43 450 300 subtest 1;
#X obj 74 84 rfft~;
#X obj 201 58 block~ 256;
#X restore 71 104 pd subtest;
"""
    )
    graph = PdParser().graph_from_file(pd_path)
    assert graph.block_size is None
    assert graph.to_hv().block_size == 64

    subtest = next(o for o in graph.get_objects() if getattr(o, "subpatch_name", None) == "subtest")
    assert subtest.block_size == 256
    assert subtest.to_hv().block_size == 256

    rfft_obj = next(o for o in subtest.get_objects() if isinstance(o, PdGraph))
    assert rfft_obj.block_size == 256
    assert rfft_obj.to_hv().block_size == 256
