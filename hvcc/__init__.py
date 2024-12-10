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

import argparse
from collections import OrderedDict
import importlib
import inspect
import json
import os
import re
import sys
import time
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
    CompilerResp, CompilerNotif, CompilerMsg, Generator,
    ExternInfo, ExternMemoryPool, ExternMidi, ExternEvents, ExternParams
)
from hvcc.types.IR import IRGraph
from hvcc.types.meta import Meta


class Colours:
    purple = "\033[95m"
    cyan = "\033[96m"
    dark_cyan = "\033[36m"
    blue = "\033[94m"
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold = "\033[1m"
    underline = "\033[4m"
    end = "\033[0m"


def add_error(
        results: Dict[str, CompilerResp],
        error: str
) -> Dict[str, CompilerResp]:
    if "hvcc" in results:
        results["hvcc"].notifs.errors.append(CompilerMsg(message=error))
    else:
        results["hvcc"] = CompilerResp(stage="hvcc",
                                       notifs=CompilerNotif(
                                          has_error=True,
                                          errors=[CompilerMsg(message=error)],
                                       ))
    return results


def check_extern_name_conflicts(extern_type: str, extern_list: List, results: OrderedDict) -> None:
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


def check_midi_objects(hvir: IRGraph) -> Dict[str, List[str]]:
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


def generate_extern_info(hvir: IRGraph, results: OrderedDict) -> ExternInfo:
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
    midi_objects = check_midi_objects(hvir)

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


def load_ext_generator(module_name, verbose) -> Optional[Generator]:
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
    search_paths: Optional[List] = None,
    generators: Optional[List] = None,
    ext_generators: Optional[List] = None,
    verbose: bool = False,
    copyright: Optional[str] = None,
    nodsp: Optional[bool] = False
) -> Dict[str, CompilerResp]:
    results: OrderedDict[str, CompilerResp] = OrderedDict()  # default value, empty dictionary
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

    if in_path.endswith((".pd")):
        if verbose:
            print("--> Generating C")
        results["pd2hv"] = pd2hv.pd2hv.compile(
            pd_path=in_path,
            hv_dir=os.path.join(out_dir, "hv"),
            search_paths=search_paths,
            verbose=verbose)

        # check for errors

        response: CompilerResp = list(results.values())[0]

        if response.notifs.has_error:
            return results

        subst_name = re.sub(r'\W', '_', patch_name)
        results["hv2ir"] = hv2ir.hv2ir.compile(
            hv_file=os.path.join(response.out_dir, response.out_file),
            # ensure that the ir filename has no funky characters in it
            ir_file=os.path.join(out_dir, "ir", f"{subst_name}.heavy.ir.json"),
            patch_name=patch_name,
            verbose=verbose)

        # check for errors
        if results["hv2ir"].notifs.has_error:
            return results

        # get the hvir data
        hvir = results["hv2ir"].ir
        assert hvir is not None
        patch_name = hvir.name.escaped
        externs = generate_extern_info(hvir, results)

        # get application path
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            application_path = os.path.join(sys._MEIPASS, 'hvcc')
        elif __file__:
            application_path = os.path.dirname(__file__)

        c_src_dir = os.path.join(out_dir, "c")
        results["ir2c"] = ir2c.ir2c.compile(
            hv_ir_path=os.path.join(results["hv2ir"].out_dir, results["hv2ir"].out_file),
            static_dir=os.path.join(application_path, "generators/ir2c/static"),
            output_dir=c_src_dir,
            externs=externs,
            copyright=copyright,
            nodsp=nodsp)

        # check for errors
        if results["ir2c"].notifs.has_error:
            return results

        # ir2c_perf
        results["ir2c_perf"] = CompilerResp(
            stage="ir2c_perf",
            obj_perf=ir2c_perf.ir2c_perf.perf(hvir, verbose=verbose),
            in_dir=results["hv2ir"].out_dir,
            in_file=results["hv2ir"].out_file,
        )

        # reconfigure such that next stage is triggered
        in_path = c_src_dir

    if os.path.isdir(in_path) and os.path.basename(in_path) == "c":
        # the c code is provided
        c_src_dir = in_path
        if hvir is None:
            # if hvir ir not provided, load it from the ir path
            try:
                # hvir_dir == project/c/../ir == project/ir
                hvir_dir = os.path.join(in_path, "..", "ir")
                hvir_path = os.path.join(hvir_dir, os.listdir(hvir_dir)[0])
                if os.path.isfile(hvir_path):
                    with open(hvir_path, "r") as f:
                        hvir = IRGraph(**json.load(f))
                        patch_name = hvir.name.escaped
                        externs = generate_extern_info(hvir, results)
                else:
                    return add_error(results, "Cannot find hvir file.")
            except Exception as e:
                return add_error(results, f"ir could not be found or loaded: {e}.")

    assert hvir is not None
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
        results["c2js"] = c2js.c2js.compile(**gen_args)

    if "daisy" in generators:
        if verbose:
            print("--> Generating Daisy module")
        results["c2daisy"] = c2daisy.c2daisy.compile(**gen_args)

    if "dpf" in generators:
        if verbose:
            print("--> Generating DPF plugin")
        results["c2dpf"] = c2dpf.c2dpf.compile(**gen_args)

    if "owl" in generators:
        if verbose:
            print("--> Generating OWL plugin")
        results["c2owl"] = c2owl.c2owl.compile(**gen_args)

    if "pdext" in generators:
        if verbose:
            print("--> Generating Pd external")
        results["c2pdext"] = c2pdext.c2pdext.compile(**gen_args)

    if "unity" in generators:
        if verbose:
            print("--> Generating Unity plugin")
        results["c2unity"] = c2unity.c2unity.compile(**gen_args)

    if "wwise" in generators:
        if verbose:
            print("--> Generating Wwise plugin")
        results["c2wwise"] = c2wwise.c2wwise.compile(**gen_args)

    if ext_generators:
        for module_name in ext_generators:
            generator = load_ext_generator(module_name, verbose)
            if generator is not None:
                if verbose:
                    print(f"--> Executing custom generator from module {module_name}")
                results[module_name] = generator.compile(**gen_args)

    return results


def main() -> bool:
    tick = time.time()

    parser = argparse.ArgumentParser(
        description="This is the Enzien Audio Heavy compiler. It compiles supported dataflow languages into C,"
                    " and other supported frameworks.")
    parser.add_argument(
        "in_path",
        help="The input dataflow file.")
    parser.add_argument(
        "-o",
        "--out_dir",
        help="Build output path.")
    parser.add_argument(
        "-p",
        "--search_paths",
        nargs="+",
        help="Add a list of directories to search through for abstractions.")
    parser.add_argument(
        "-n",
        "--name",
        default="heavy",
        help="Provides a name for the generated Heavy context.")
    parser.add_argument(
        "-m",
        "--meta",
        help="Provide metadata file (json) for generator")
    parser.add_argument(
        "-g",
        "--gen",
        nargs="+",
        default=["c"],
        help="List of generator outputs: c, unity, wwise, js, pdext, daisy, dpf, fabric, owl")
    parser.add_argument(
        "-G",
        "--ext-gen",
        nargs="*",
        help="List of external generator modules, see 'External Generators' docs page.")
    parser.add_argument(
        "--results_path",
        help="Write results dictionary to the given path as a JSON-formatted string."
             " Target directory will be created if it does not exist.")
    parser.add_argument(
        "--nodsp",
        action='store_true',
        help="Disable DSP. Run as control-only patch."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show debugging information.",
        action="count")
    parser.add_argument(
        "--copyright",
        help="A string indicating the owner of the copyright.")
    args = parser.parse_args()

    in_path = os.path.abspath(args.in_path)
    results = compile_dataflow(
        in_path=in_path,
        out_dir=args.out_dir or os.path.dirname(in_path),
        patch_name=args.name,
        patch_meta_file=args.meta,
        search_paths=args.search_paths,
        generators=args.gen,
        ext_generators=args.ext_gen,
        verbose=args.verbose,
        copyright=args.copyright,
        nodsp=args.nodsp
    )

    errorCount = 0
    for r in list(results.values()):
        # print any errors
        if r.notifs.has_error:
            for i, error in enumerate(r.notifs.errors):
                errorCount += 1
                print("{4:3d}) {2}Error{3} {0}: {1}".format(
                    r.stage, error.message, Colours.red, Colours.end, i + 1))

            # only print exception if no errors are indicated
            if len(r.notifs.errors) == 0 and r.notifs.exception is not None:
                errorCount += 1
                print("{2}Error{3} {0} exception: {1}".format(
                    r.stage, r.notifs.exception, Colours.red, Colours.end))

            # clear any exceptions such that results can be JSONified if necessary
            r.notifs.exception = None

        # print any warnings
        for i, warning in enumerate(r.notifs.warnings):
            print("{4:3d}) {2}Warning{3} {0}: {1}".format(
                r.stage, warning.message, Colours.yellow, Colours.end, i + 1))

    if args.results_path:
        results_path = os.path.realpath(os.path.abspath(args.results_path))
        results_dir = os.path.dirname(results_path)

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        with open(results_path, "w") as f:
            json.dump(results, f)

    if args.verbose:
        print("Total compile time: {0:.2f}ms".format(1000 * (time.time() - tick)))
    return errorCount != 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
