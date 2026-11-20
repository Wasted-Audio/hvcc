"""Signal comparisons (<~, >~, ==~, ...) must output 1.0 or 0.0.

With SIMD the IR comparison objects (__lt~f etc.) return a bit mask (all bits set for true),
so hv2ir masks the result of Pd's comparison objects with 1.0: [__lt~f] -> [__and~f 1.0].
The IR objects themselves keep their mask semantics, which lib patches rely on.

These tests check the generated IR, so they do not depend on the SIMD variant the test
machine builds.
"""

import json
from pathlib import Path

import pytest

from hvcc.compiler import compile_dataflow
from hvcc.types.IR import IRBuffer, IRGraph, IRSignalList

COMPARISONS = {
    "<~": "__lt~f",
    "<=~": "__lte~f",
    ">~": "__gt~f",
    ">=~": "__gte~f",
    "==~": "__eq~f",
    "!=~": "__neq~f",
}


def compile_ir(tmp_path: Path, obj: str, right_inlet: bool) -> IRGraph:
    """Compile [adc~ 1 2] -> [obj] -> [dac~ 1] and return the IR.

    obj: the object's Pd text, or the lines of an @hv_obj subpatch ending in "#X restore".
    right_inlet: connect the second input channel to the right inlet of obj.
    """
    obj_line = obj if obj.startswith("#N canvas") else f"#X obj 30 80 {obj};\n"
    pd_path = tmp_path / "comparison.pd"
    lines = [
        "#N canvas 0 0 450 300 12;\n",
        "#X obj 30 30 adc~ 1 2;\n",
        obj_line,
        "#X obj 30 130 dac~ 1;\n",
        "#X connect 0 0 1 0;\n",
        "#X connect 0 1 1 1;\n" if right_inlet else "",
        "#X connect 1 0 2 0;\n",
    ]

    pd_path.write_text("".join(lines))
    out_dir = tmp_path / "out"
    results = compile_dataflow(pd_path, out_dir, verbose=False)

    for stage, result in results.root.items():
        assert not result.notifs.has_error, f"{stage}: {result.notifs}"

    with open(out_dir / "ir" / "heavy.heavy.ir.json") as f:
        return IRGraph(**json.load(f))


def first_reader(process_order: list[IRSignalList], start: int, buffer: IRBuffer) -> IRSignalList | None:
    """The first object after process_order[start] that reads buffer, before it is overwritten."""
    for entry in process_order[start + 1:]:
        if buffer in entry.inputBuffers:
            return entry
        if buffer in entry.outputBuffers:
            return None
    return None


def masked_comparisons(ir: IRGraph, ir_type: str) -> list[bool]:
    """For every IR object of ir_type: is its output masked with [__and~f] and the constant 1.0?"""
    objects = ir.objects
    order = ir.signal.processOrder
    masked = []
    for i, entry in enumerate(order):
        if objects[entry.id].type != ir_type:
            continue
        reader = first_reader(order, i, entry.outputBuffers[0])
        ok = reader is not None and objects[reader.id].type == "__and~f"
        assert reader

        if ok:
            # the other input of __and~f is the constant 1.0
            other = [b for b in reader.inputBuffers if b != entry.outputBuffers[0]]
            producers = [e for e in order[:order.index(reader)] if other and other[0] in e.outputBuffers]
            ok = bool(producers) and objects[producers[-1].id].type == "__var_k~f" \
                and objects[producers[-1].id].args["k"] == 1.0
        masked.append(ok)
    return masked


@pytest.mark.parametrize("pd_obj", COMPARISONS)
def test_signal_comparison_is_masked(tmp_path: Path, pd_obj: str):
    # [<~] with a signal in the right inlet
    ir = compile_ir(tmp_path, pd_obj, right_inlet=True)
    assert masked_comparisons(ir, COMPARISONS[pd_obj]) == [True]


@pytest.mark.parametrize("pd_obj", COMPARISONS)
def test_signal_comparison_with_argument_is_masked(tmp_path: Path, pd_obj: str):
    # [<~ 2]: the right operand is a constant
    ir = compile_ir(tmp_path, f"{pd_obj} 2", right_inlet=False)
    assert masked_comparisons(ir, COMPARISONS[pd_obj]) == [True]


def test_ir_comparison_keeps_mask(tmp_path: Path):
    # [@hv_obj __lt~f] is the IR object itself (as used in lib patches): its bit mask is not changed
    hv_obj = (
        "#N canvas 0 0 450 300 @hv_obj 0;\n"
        "#X obj 10 10 inlet~;\n"
        "#X obj 100 10 inlet~;\n"
        "#X obj 10 60 outlet~;\n"
        "#X restore 30 80 pd @hv_obj __lt~f;\n"
    )
    ir = compile_ir(tmp_path, hv_obj, right_inlet=True)
    assert masked_comparisons(ir, "__lt~f") == [False]
    assert not [o for o in ir.objects.values() if o.type == "__and~f"]
