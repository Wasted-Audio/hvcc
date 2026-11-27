from pathlib import Path

from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.interpreters.pd2hv.PdTriggerObject import PdTriggerObject
from hvcc.types.Heavy import HvConn


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
    assert not graph.get_notices().has_error

    faustgen_object = graph.to_hv()
    object = next(iter(faustgen_object.objects.items()))
    assert object[1].args["faustpatch"] == "gain"


def test_faustgen_iolets(tmp_path: Path):
    pd_path = tmp_path / "faust_patch.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 144 126 faustgen2~ gain;
#X obj 144 67 loadbang;
#X obj 144 158 print;
#X obj 287 67 osc~ 220;
#X obj 287 158 dac~ 1;
#X msg 144 93 gain 1;
#X connect 0 0 2 0;
#X connect 0 1 4 0;
#X connect 1 0 5 0;
#X connect 3 0 0 1;
#X connect 5 0 0 0;
""")

    graph = PdParser().graph_from_file(pd_path)
    assert not graph.get_notices().has_error
    graph.validate_configuration()

    hv_graph = graph.to_hv()
    faustgen_object = next(iter(hv_graph.objects))

    connections: list[HvConn] = hv_graph.connections

    for conn in connections:
        if (conn.conn_from.id == faustgen_object and conn.conn_from.outlet == 0) or \
           (conn.conn_to.id == faustgen_object and conn.conn_to.inlet == 0):
            assert conn.type == '-->'

        if (conn.conn_from.id == faustgen_object and conn.conn_from.outlet >= 1) or \
           (conn.conn_to.id == faustgen_object and conn.conn_to.inlet >= 1):
            assert conn.type == '~f>'
