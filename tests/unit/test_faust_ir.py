import json
from pathlib import Path

from hvcc.core.hv2ir.hv2ir import hv2ir
from hvcc.interpreters.pd2hv.pd2hv import pd2hv
from hvcc.interpreters.pd2hv.PdParser import PdParser
from hvcc.types.Heavy import Heavy, HvConn, HvConnFrom, HvConnTo
from hvcc.types.IR import IRBuffer, IRGraph, IROnMessage


def compile_hv_to_ir(tmp_path: Path, hv_graph: Heavy) -> IRGraph:
    """Compile a HeavyLang graph to HeavyIR and return the parsed IRGraph."""
    hv_file = tmp_path / "faust.hv.json"
    ir_file = tmp_path / "faust.heavy.ir.json"
    hv_file.write_text(hv_graph.model_dump_json(by_alias=True, indent=2))

    resp = hv2ir.compile(hv_file, ir_file, patch_name="faust_test")
    assert not resp.notifs.has_error, resp.notifs
    assert not resp.notifs.errors, resp.notifs

    return IRGraph(**json.loads(ir_file.read_text()))


def compile_pd_to_ir(tmp_path: Path, pd_text: str) -> IRGraph:
    """Compile a Pd patch through pd2hv and hv2ir and return the parsed IRGraph."""
    pd_file = tmp_path / "faust_patch.pd"
    pd_file.write_text(pd_text)

    hv_dir = tmp_path / "hv"
    pd_resp = pd2hv.compile(pd_file, hv_dir)
    assert not pd_resp.notifs.has_error, pd_resp.notifs
    assert not pd_resp.notifs.errors, pd_resp.notifs

    ir_file = tmp_path / "ir" / "faust_patch.heavy.ir.json"
    ir_resp = hv2ir.compile(hv_dir / "faust_patch.hv.json", ir_file, patch_name="faust_patch")
    assert not ir_resp.notifs.has_error, ir_resp.notifs
    assert not ir_resp.notifs.errors, ir_resp.notifs

    return IRGraph(**json.loads(ir_file.read_text()))


def obj_id_from_type(ir: IRGraph, obj_type: str) -> str:
    return next(
        obj_id for obj_id, obj in ir.objects.items() if obj.type == obj_type
    )


def test_faustgen_ir_base(tmp_path: Path):
    pd_path = tmp_path / "faust_ir.pd"
    pd_path.write_text(
        """#N canvas 827 239 734 565 12;
#X obj 144 126 faustgen2~ stereogain;
#X obj 287 67 osc~ 220;
#X obj 287 158 dac~ 1 2;
#X connect 1 0 0 1;
#X connect 0 1 2 0;
#X connect 0 2 2 1;
""")

    graph = PdParser().graph_from_file(pd_path)
    assert not graph.get_notices().errors

    hv_path = tmp_path / "faust_ir.hv.json"
    hv_path.write_text(graph.to_hv().model_dump_json(by_alias=True))

    result = hv2ir.compile(hv_path, tmp_path / "faust_ir.ir.json")
    assert not result.notifs.has_error
    assert not result.notifs.errors


def test_faustgen_ir_object_and_init(tmp_path: Path):
    hv_graph = Heavy(
        type="graph",
        objects={
            "faust": Heavy(
                type="__faustgen2~",
                args={
                    "faustpatch": "gain",
                    "num_inlets": 2,
                    "num_outlets": 2,
                },
            ),
            "dac~": Heavy(type="dac", args={"channels": [1]}),
        },
        connections=[
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="faust", outlet=1),
                conn_to=HvConnTo(id="dac~", inlet=0),
            ),
        ],
    )

    ir = compile_hv_to_ir(tmp_path, hv_graph)

    faust_id, faust_obj = next(
        (obj_id, obj) for obj_id, obj in ir.objects.items() if obj.type == "__faustgen2~"
    )

    assert faust_id in ir.init.order
    assert faust_obj.args["faustpatch"] == "gain"


def test_faustgen_ir_control_connections(tmp_path: Path):
    hv_graph = Heavy(
        type="graph",
        objects={
            "recv": Heavy(type="receive", args={"name": "param_in"},
                          annotations={"scope": "public"}),
            "faust": Heavy(
                type="__faustgen2~",
                args={
                    "faustpatch": "gain",
                    "num_inlets": 2,
                    "num_outlets": 2,
                },
            ),
            "out_print": Heavy(type="print", args={"label": "faust_out"}),
            "dac": Heavy(type="dac", args={"channels": [1]}),
        },
        connections=[
            HvConn(
                type="-->",
                conn_from=HvConnFrom(id="recv", outlet=0),
                conn_to=HvConnTo(id="faust", inlet=0),
            ),
            HvConn(
                type="-->",
                conn_from=HvConnFrom(id="faust", outlet=0),
                conn_to=HvConnTo(id="out_print", inlet=0),
            ),
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="faust", outlet=1),
                conn_to=HvConnTo(id="dac", inlet=0),
            ),
        ],
    )

    ir = compile_hv_to_ir(tmp_path, hv_graph)

    send_msgs = {msg.id: msg for msg in ir.control.sendMessage}

    faust_id = obj_id_from_type(ir, "__faustgen2~")
    recv_id = obj_id_from_type(ir, "__receive")
    print_id= obj_id_from_type(ir, "__print")

    assert IROnMessage(id=faust_id, inletIndex=0) in send_msgs[recv_id].onMessage[0]

    assert faust_id in send_msgs
    assert IROnMessage(id=print_id, inletIndex=0) in send_msgs[faust_id].onMessage[0]
    # Signal outlet (index 1) has no control targets
    assert send_msgs[faust_id].onMessage[1] == []


def test_faustgen_ir_signal_buffers_exclude_control_iolets(tmp_path: Path):
    hv_graph = Heavy(
        type="graph",
        objects={
            "recv": Heavy(type="receive", args={"name": "ctrl"},
                          annotations={"scope": "public"}),
            "adc": Heavy(type="adc", args={"channels": [1, 2]}),
            "faust": Heavy(
                type="__faustgen2~",
                args={
                    "faustpatch": "stereo_gain",
                    "num_inlets": 3,
                    "num_outlets": 3,
                },
            ),
            "out_print": Heavy(type="print", args={"label": "ctrl_out"}),
            "dac": Heavy(type="dac", args={"channels": [1, 2]}),
        },
        connections=[
            HvConn(
                type="-->",
                conn_from=HvConnFrom(id="recv", outlet=0),
                conn_to=HvConnTo(id="faust", inlet=0),
            ),
            HvConn(
                type="-->",
                conn_from=HvConnFrom(id="faust", outlet=0),
                conn_to=HvConnTo(id="out_print", inlet=0),
            ),
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="adc", outlet=0),
                conn_to=HvConnTo(id="faust", inlet=1),
            ),
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="adc", outlet=1),
                conn_to=HvConnTo(id="faust", inlet=2),
            ),
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="faust", outlet=1),
                conn_to=HvConnTo(id="dac", inlet=0),
            ),
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="faust", outlet=2),
                conn_to=HvConnTo(id="dac", inlet=1),
            ),
        ],
    )

    ir = compile_hv_to_ir(tmp_path, hv_graph)

    faust_id = obj_id_from_type(ir, "__faustgen2~")
    dacs = [obj_id for obj_id, obj in ir.objects.items() if obj.type == "__add~f"]
    dac1_id = dacs[0]
    dac2_id = dacs[1]

    process_by_id = {entry.id: entry for entry in ir.signal.processOrder}
    assert faust_id in process_by_id
    faust_entry = process_by_id[faust_id]
    dac1_entry = process_by_id[dac1_id]
    dac2_entry = process_by_id[dac2_id]

    # Control inlet/outlet 0 must not appear in signal buffers
    assert len(faust_entry.inputBuffers) == 2
    assert len(faust_entry.outputBuffers) == 2
    assert all(buf.type == "~f>" for buf in faust_entry.outputBuffers)
    assert faust_entry.outputBuffers[0] != faust_entry.outputBuffers[1]
    assert dac1_entry.inputBuffers[0] == faust_entry.outputBuffers[0]
    assert dac2_entry.inputBuffers[0] == faust_entry.outputBuffers[1]


def test_faustgen_ir_unconnected_signal_inlet_uses_zero_buffer(tmp_path: Path):
    hv_graph = Heavy(
        type="graph",
        objects={
            "faust": Heavy(
                type="__faustgen2~",
                args={
                    "faustpatch": "osc",
                    "num_inlets": 2,
                    "num_outlets": 2,
                },
            ),
            "dac": Heavy(type="dac", args={"channels": [1]}),
        },
        connections=[
            HvConn(
                type="~f>",
                conn_from=HvConnFrom(id="faust", outlet=1),
                conn_to=HvConnTo(id="dac", inlet=0),
            ),
        ],
    )

    ir = compile_hv_to_ir(tmp_path, hv_graph)
    faust_id = obj_id_from_type(ir, "__faustgen2~")

    process_by_id = {entry.id: entry for entry in ir.signal.processOrder}
    faust_entry = process_by_id[faust_id]
    assert faust_entry.inputBuffers == [IRBuffer(type="zero", index=0)]
    assert len(faust_entry.outputBuffers) == 1
    assert faust_entry.outputBuffers[0].type == "~f>"


def test_faustgen_pd_to_ir_end_to_end(tmp_path: Path):
    ir = compile_pd_to_ir(
        tmp_path,
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
""",
    )

    faust_ids = [obj_id for obj_id, obj in ir.objects.items() if obj.type == "__faustgen2~"]
    assert len(faust_ids) == 1
    faust_id = faust_ids[0]
    assert ir.objects[faust_id].args["faustpatch"] == "gain"
    assert faust_id in ir.init.order

    process_by_id = {entry.id: entry for entry in ir.signal.processOrder}
    assert faust_id in process_by_id
    assert len(process_by_id[faust_id].inputBuffers) == 1
    assert len(process_by_id[faust_id].outputBuffers) == 1

    send_msgs = {msg.id: msg for msg in ir.control.sendMessage}
    assert faust_id in send_msgs
    assert len(send_msgs[faust_id].onMessage[0]) == 1
