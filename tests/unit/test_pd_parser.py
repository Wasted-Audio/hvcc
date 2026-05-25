from hvcc.interpreters.pd2hv.PdParser import PdParser


def test_multiple_arrays_in_subpatch_parse_without_metadata_errors(tmp_path):
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
