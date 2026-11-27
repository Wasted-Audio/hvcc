from pathlib import Path

from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.interpreters.pd2hv.PdTriggerObject import PdTriggerObject


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
    notices = graph.get_notices()
    assert not notices.has_error
    assert not notices.errors

    nam_object = graph.get_objects()[0].get_objects()[1]
    assert Path(nam_object.obj_dict["nam"]) == tmp_path / "test.nam"


def test_trigger_convert_args():
    convert_args = PdTriggerObject._PdTriggerObject__convert_args  # pyright: ignore

    assert convert_args(["any"]) == ["a"]
    assert convert_args(["float"]) == ["f"]
    assert convert_args(["symbol"]) == ["s"]
    assert convert_args(["bang"]) == ["b"]
    assert convert_args(["unknown"]) == ["unknown"]


def test_faustgen_patch(tmp_path: Path):
    pd_path = tmp_path / "faust_patch.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 86 129 faustgen2~ gain;
""")

    graph = PdParser().graph_from_file(pd_path)
    notices = graph.get_notices()
    assert not notices.has_error
    assert not notices.errors

    hv_graph = graph.to_hv()
    _, obj = next(iter(hv_graph.objects.items()))
    assert obj.type == "__faustgen2~"
    assert obj.args["faustpatch"] == "gain"


def test_faustgen_args_errors(tmp_path: Path):
    no_arg_path = tmp_path / "faust_no_arg.pd"
    no_arg_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 86 129 faustgen2~;
""")

    graph = PdParser().graph_from_file(no_arg_path)
    notices = graph.get_notices()
    assert len(notices.errors) == 1
    assert "No patch arguments" in notices.errors[0].message

    multi_arg_path = tmp_path / "faust_multi_arg.pd"
    multi_arg_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 86 129 faustgen2~ gain extra;
""")

    graph = PdParser().graph_from_file(multi_arg_path)
    notices = graph.get_notices()
    assert len(notices.errors) == 1
    assert "Only a single patch argument is allowed" in notices.errors[0].message


def test_faustgen_iolets(tmp_path: Path):
    pd_path = tmp_path / "faust_iolets.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 144 126 faustgen2~ stereogain;
#X obj 144 67 loadbang;
#X obj 144 158 print;
#X obj 287 67 osc~ 220;
#X obj 287 158 dac~ 1 2;
#X msg 144 93 gain 1;
#X connect 0 0 2 0;
#X connect 0 1 4 0;
#X connect 0 2 4 1;
#X connect 1 0 5 0;
#X connect 3 0 0 1;
#X connect 3 0 0 2;
#X connect 5 0 0 0;
""")

    graph = PdParser().graph_from_file(pd_path)
    notices = graph.get_notices()
    assert not notices.has_error
    assert not notices.errors

    hv_graph = graph.to_hv()
    faustgen_id = next(
        obj_id for obj_id, obj in hv_graph.objects.items() if obj.type == "__faustgen2~"
    )

    inlet_types = {
        conn.conn_to.inlet: conn.type
        for conn in hv_graph.connections
        if conn.conn_to.id == faustgen_id
    }
    outlet_types = {
        conn.conn_from.outlet: conn.type
        for conn in hv_graph.connections
        if conn.conn_from.id == faustgen_id
    }

    assert inlet_types == {0: "-->", 1: "~f>", 2: "~f>"}
    assert outlet_types == {0: "-->", 1: "~f>", 2: "~f>"}


def test_faustgen_mixed_inlets(tmp_path: Path):
    pd_path = tmp_path / "faust_mixed_inlets.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#N canvas 0 0 200 200 mixed0 0;
#X obj 10 10 outlet -~>;
#X restore 50 50 pd mixed0;
#N canvas 0 0 200 200 mixed1 0;
#X obj 10 10 outlet -~>;
#X restore 150 50 pd mixed1;
#X obj 100 120 faustgen2~ gain;
#X connect 0 0 2 0;
#X connect 1 0 2 1;
""")

    graph = PdParser().graph_from_file(pd_path)
    notices = graph.get_notices()
    assert not notices.has_error
    assert not notices.errors

    hv_graph = graph.to_hv()
    faustgen_id = next(
        obj_id for obj_id, obj in hv_graph.objects.items() if obj.type == "__faustgen2~"
    )

    inlet_types = {
        conn.conn_to.inlet: conn.type
        for conn in hv_graph.connections
        if conn.conn_to.id == faustgen_id
    }
    assert inlet_types == {0: "-->", 1: "~f>"}
