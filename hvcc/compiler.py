# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2021-2024 Wasted Audio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import inspect
import json
import os
import re
import sys
from typing import Any, List, Dict, Optional

from hvcc.interpreters.pd2hv import pd2hv
from hvcc.core.hv2ir import hv2ir
from hvcc.generators.ir2c import ir2c
from hvcc.generators.ir2c import ir2c_perf
from hvcc.generators.c2js import c2js
from hvcc.generators.c2daisy import c2daisy
from hvcc.generators.c2dpf import c2dpf
from hvcc.generators.c2owl import c2owl
from hvcc.generators.c2pdext import c2pdext
from hvcc.generators.c2wwise import c2wwise
from hvcc.generators.c2unity import c2unity
from hvcc.types.compiler import (
    CompilerResults, CompilerResp, CompilerNotif, CompilerMsg, Generator,
    ExternInfo, ExternMemoryPool, ExternMidi, ExternEvents, ExternParams
)
from hvcc.types.IR import IRGraph
from hvcc.types.meta import Meta


def add_error(
    results: CompilerResults,
    error: str
) -> CompilerResults:
    if "hvcc" in results.root:
        results.root["hvcc"].notifs.errors.append(CompilerMsg(message=error))
    else:
        results.root["hvcc"] = CompilerResp(
                                stage="hvcc",
                                notifs=CompilerNotif(
                                    has_error=True,
                                    errors=[CompilerMsg(message=error)]
                                )
                            )
    return results


def check_extern_name_conflicts(extern_type: str, extern_list: List, results: CompilerResults) -> None:
    """ In most of the generator code extern names become capitalised when used
        as enums. This method makes sure that there are no cases where two unique
        keys become the same after being capitalised.
        Note(joe): hvcc is probably the best place to check as at this point we
        have a list of all extern names.
    """
    for i, v in enumerate(extern_list):
        for j, u in enumerate(extern_list[i + 1:]):
            if v[0].upper() == u[0].upper():
                add_error(results,
                          f"Conflicting {extern_type} names '{v[0]}' and '{u[0]}', make sure that "
                          "capital letters are not the only difference.")


def count_midi_objects(hvir: IRGraph) -> Dict[str, List[str]]:
    in_midi = []
    out_midi = []

    midi_in_objs = [
        '__hv_bendin',
        '__hv_ctlin',
        '__hv_midiin',
        '__hv_midirealtimein',
        '__hv_notein',
        '__hv_pgmin',
        '__hv_polytouchin',
        '__hv_touchin',
    ]

    midi_out_objs = [
        '__hv_bendout',
        '__hv_ctlout',
        '__hv_midiout',
        '__hv_midioutport',
        '__hv_noteout',
        '__hv_pgmout',
        '__hv_polytouchout',
        '__hv_touchout',
    ]

    for recv in hvir.control.receivers.keys():
        if recv in midi_in_objs:
            in_midi.append(recv)

    for msg in hvir.control.sendMessage:
        if msg.name in midi_out_objs:
            out_midi.append(msg.name)

    return {
        'in': in_midi,
        'out': out_midi
    }


def filter_midi_from_out_parameters(output_parameter_list: List, midi_out_objects: List) -> List:
    new_out_list = []

    for item in output_parameter_list:
        if not item[0] in midi_out_objects:
            new_out_list.append(item)

    return new_out_list


def generate_extern_info(hvir: IRGraph, results: CompilerResults) -> ExternInfo:
    """ Simplifies the receiver/send and table lists by only containing values
        externed with @hv_param, @hv_event or @hv_table
    """
    # Exposed input parameters
    in_parameter_list = [(k, v) for k, v in hvir.control.receivers.items() if v.extern == "param"]
    in_parameter_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("input parameter", in_parameter_list, results)

    # Exposed input events
    in_event_list = [(k, v) for k, v in hvir.control.receivers.items() if v.extern == "event"]
    in_event_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("input event", in_event_list, results)

    # Exposed output parameters
    out_parameter_list = [(v.name, v) for v in hvir.control.sendMessage if v.extern == "param"]
    # remove duplicate output parameters/events
    # NOTE(joe): is the id argument important here? We'll only take the first one in this case.
    out_parameter_list = list(dict(out_parameter_list).items())
    out_parameter_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("output parameter", out_parameter_list, results)

    # Exposed output events
    out_event_list = [(v.name, v) for v in hvir.control.sendMessage if v.extern == "event"]
    out_event_list = list(dict(out_event_list).items())
    out_event_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("output event", out_event_list, results)

    # Exposed tables
    table_list = [(k, v) for k, v in hvir.tables.items() if v.extern]
    table_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("table", table_list, results)

    # Exposed midi objects
    midi_objects = count_midi_objects(hvir)

    # filter midi objects from the output parameters list
    out_parameter_list = filter_midi_from_out_parameters(out_parameter_list, midi_objects['out'])

    return ExternInfo(
        parameters=ExternParams(
            inParam=in_parameter_list,
            outParam=out_parameter_list
        ),
        events=ExternEvents(
            inEvent=in_event_list,
            outEvent=out_event_list
        ),
        midi=ExternMidi(
            inMidi=midi_objects['in'],
            outMidi=midi_objects['out']
        ),
        tables=table_list,
        # generate patch heuristics to ensure enough memory allocated for the patch
        memoryPoolSizesKb=ExternMemoryPool(
            internal=10,  # TODO(joe): should this increase if there are a lot of internal connections?
            inputQueue=max(2, int(
                len(in_parameter_list) +
                (len(in_event_list) / 4) +
                len(midi_objects['in'])  # TODO(dreamer): should this depend on the MIDI type?
            )),
            outputQueue=max(2, int(
                len(out_parameter_list) +
                (len(out_event_list) / 4) +
                len(midi_objects['out'])
            ))
        )
    )


def load_ext_generator(module_name: str, verbose: bool) -> Optional[Generator]:
    try:
        module = importlib.import_module(module_name)
        for _, member in inspect.getmembers(module):
            if inspect.isclass(member) and not inspect.isabstract(member) and issubclass(member, Generator):
                return member()
        if verbose:
            print(f"---> Module {module_name} does not contain a class derived from hvcc.types.Compiler")
        return None
    except ModuleNotFoundError:
        return None


def compile_dataflow(
    in_path: str,
    out_dir: str,
    patch_name: str = "heavy",
    patch_meta_file: Optional[str] = None,
    search_paths: Optional[List[str]] = None,
    generators: Optional[List[str]] = None,
    ext_generators: Optional[List[str]] = None,
    verbose: bool = False,
    copyright: Optional[str] = None,
    nodsp: Optional[bool] = False
) -> CompilerResults:
    results = CompilerResults(root={})
    patch_meta = Meta()

    # basic error checking on input
    if os.path.isfile(in_path):
        if not in_path.endswith((".pd")):
            return add_error(results, "Can only process Pd files.")
    elif os.path.isdir(in_path):
        if not os.path.basename("c"):
            return add_error(results, "Can only process c directories.")
    else:
        return add_error(results, f"Unknown input path {in_path}")

    # meta-data file
    if patch_meta_file:
        if os.path.isfile(patch_meta_file):
            with open(patch_meta_file) as json_file:
                try:
                    patch_meta_json = json.load(json_file)
                    patch_meta = Meta(**patch_meta_json)
                except Exception as e:
                    return add_error(results, f"Unable to open json_file: {e}")

    patch_name = patch_meta.name or patch_name
    generators = ["c"] if generators is None else [x.lower() for x in generators]

    if verbose:
        print("--> Generating C")
    results.root["pd2hv"] = pd2hv.pd2hv.compile(
        pd_path=in_path,
        hv_dir=os.path.join(out_dir, "hv"),
        search_paths=search_paths,
        verbose=verbose)

    # check for errors
    response: CompilerResp = list(results.root.values())[0]

    if response.notifs.has_error:
        return results

    subst_name = re.sub(r'\W', '_', patch_name)
    results.root["hv2ir"] = hv2ir.hv2ir.compile(
        hv_file=os.path.join(response.out_dir, response.out_file),
        # ensure that the ir filename has no funky characters in it
        ir_file=os.path.join(out_dir, "ir", f"{subst_name}.heavy.ir.json"),
        patch_name=patch_name,
        verbose=verbose)

    # check for errors
    if results.root["hv2ir"].notifs.has_error:
        return results

    # get the hvir data
    hvir = results.root["hv2ir"].ir
    assert hvir is not None
    patch_name = hvir.name.escaped
    externs = generate_extern_info(hvir, results)

    # get application path
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        application_path = os.path.join(sys._MEIPASS, 'hvcc')
    elif __file__:
        application_path = os.path.dirname(__file__)

    c_src_dir = os.path.join(out_dir, "c")
    results.root["ir2c"] = ir2c.ir2c.compile(
        hv_ir_path=os.path.join(results.root["hv2ir"].out_dir, results.root["hv2ir"].out_file),
        static_dir=os.path.join(application_path, "generators/ir2c/static"),
        output_dir=c_src_dir,
        externs=externs,
        copyright=copyright,
        nodsp=nodsp)

    # check for errors
    if results.root["ir2c"].notifs.has_error:
        return results

    # ir2c_perf
    results.root["ir2c_perf"] = CompilerResp(
        stage="ir2c_perf",
        obj_perf=ir2c_perf.ir2c_perf.perf(hvir, verbose=verbose),
        in_dir=results.root["hv2ir"].out_dir,
        in_file=results.root["hv2ir"].out_file,
    )

    # run the c2x generators, merge the results
    num_input_channels = hvir.signal.numInputBuffers
    num_output_channels = hvir.signal.numOutputBuffers

    gen_args: Dict[str, Any] = {
        'c_src_dir': c_src_dir,
        'out_dir': out_dir,
        'patch_name': patch_name,
        'patch_meta': patch_meta,
        'num_input_channels': num_input_channels,
        'num_output_channels': num_output_channels,
        'externs': externs,
        'copyright': copyright,
        'verbose': verbose
    }

    if "js" in generators:
        if verbose:
            print("--> Generating Javascript")
        results.root["c2js"] = c2js.c2js.compile(**gen_args)

    if "daisy" in generators:
        if verbose:
            print("--> Generating Daisy module")
        results.root["c2daisy"] = c2daisy.c2daisy.compile(**gen_args)

    if "dpf" in generators:
        if verbose:
            print("--> Generating DPF plugin")
        results.root["c2dpf"] = c2dpf.c2dpf.compile(**gen_args)

    if "owl" in generators:
        if verbose:
            print("--> Generating OWL plugin")
        results.root["c2owl"] = c2owl.c2owl.compile(**gen_args)

    if "pdext" in generators:
        if verbose:
            print("--> Generating Pd external")
        results.root["c2pdext"] = c2pdext.c2pdext.compile(**gen_args)

    if "unity" in generators:
        if verbose:
            print("--> Generating Unity plugin")
        results.root["c2unity"] = c2unity.c2unity.compile(**gen_args)

    if "wwise" in generators:
        if verbose:
            print("--> Generating Wwise plugin")
        results.root["c2wwise"] = c2wwise.c2wwise.compile(**gen_args)

    if ext_generators:
        for module_name in ext_generators:
            generator = load_ext_generator(module_name, verbose)
            if generator is not None:
                if verbose:
                    print(f"--> Executing custom generator from module {module_name}")
                results.root[module_name] = generator.compile(**gen_args)

    return results
