# Copyright (C) 2014-2018 Enzien Audio, Ltd.
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
import json
import os
import re
import time

from hvcc.interpreters.pd2hv import pd2hv
from hvcc.interpreters.max2hv import max2hv
from hvcc.core.hv2ir import hv2ir
from hvcc.generators.ir2c import ir2c
from hvcc.generators.ir2c import ir2c_perf
from hvcc.generators.c2bela import c2bela
from hvcc.generators.c2fabric import c2fabric
from hvcc.generators.c2js import c2js
from hvcc.generators.c2daisy import c2daisy
from hvcc.generators.c2dpf import c2dpf
from hvcc.generators.c2pdext import c2pdext
from hvcc.generators.c2wwise import c2wwise
from hvcc.generators.c2unity import c2unity


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


def add_error(results, error):
    if "hvcc" in results:
        results["hvcc"]["notifs"]["errors"].append({"message": error})
    else:
        results["hvcc"] = {
            "stage": "hvcc",
            "notifs": {
                "has_error": True,
                "exception": None,
                "errors": [{"message": error}],
                "warnings": []
            }
        }
    return results


def check_extern_name_conflicts(extern_type, extern_list, results):
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
                          "Conflicting {0} names '{1}' and '{2}', make sure that "
                          "capital letters are not the only difference.".format(extern_type, v[0], u[0]))


def generate_extern_info(hvir, results):
    """ Simplifies the receiver/send and table lists by only containing values
        externed with @hv_param, @hv_event or @hv_table
    """
    # Exposed input parameters
    in_parameter_list = [(k, v) for k, v in hvir["control"]["receivers"].items() if v.get("extern", None) == "param"]
    in_parameter_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("input parameter", in_parameter_list, results)

    # Exposed input events
    in_event_list = [(k, v) for k, v in hvir["control"]["receivers"].items() if v.get("extern", None) == "event"]
    in_event_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("input event", in_event_list, results)

    # Exposed output parameters
    out_parameter_list = [(v["name"], v) for v in hvir["control"]["sendMessage"] if v.get("extern", None) == "param"]
    # remove duplicate output parameters/events
    # NOTE(joe): is the id argument important here? We'll only take the first one in this case.
    out_parameter_list = list(dict(out_parameter_list).items())
    out_parameter_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("output parameter", out_parameter_list, results)

    # Exposed output events
    out_event_list = [(v["name"], v) for v in hvir["control"]["sendMessage"] if v.get("extern", None) == "event"]
    out_event_list = list(dict(out_event_list).items())
    out_event_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("output event", out_event_list, results)

    # Exposed tables
    table_list = [(k, v) for k, v in hvir["tables"].items() if v.get("extern", None)]
    table_list.sort(key=lambda x: x[0])
    check_extern_name_conflicts("table", table_list, results)

    return {
        "parameters": {
            "in": in_parameter_list,
            "out": out_parameter_list
        },
        "events": {
            "in": in_event_list,
            "out": out_event_list
        },
        "tables": table_list,
        # generate patch heuristics to ensure enough memory allocated for the patch
        "memoryPoolSizesKb": {
            "internal": 10,  # TODO(joe): should this increase if there are a lot of internal connections?
            "inputQueue": max(2, int(len(in_parameter_list) + len(in_event_list) / 4)),
            "outputQueue": max(2, int(len(out_parameter_list) + len(out_event_list) / 4)),
        }
    }


def compile_dataflow(in_path, out_dir, patch_name=None, patch_meta_file=None,
                     search_paths=None, generators=None, verbose=False,
                     copyright=None, hvir=None):

    results = OrderedDict()  # default value, empty dictionary

    # basic error checking on input
    if os.path.isfile(in_path):
        if not in_path.endswith((".pd", ".maxpat")):
            return add_error(results, "Can only process Pd or Max files.")
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
                    patch_meta = json.load(json_file)
                except Exception as e:
                    return add_error(results, f"Unable to open json_file: {e}")
    else:
        patch_meta = {}

    patch_name = patch_name or "heavy"
    generators = generators or {"c"}

    if in_path.endswith((".pd", ".maxpat")):
        if verbose:
            print("--> Generating C")
        if in_path.endswith(".pd"):
            results["pd2hv"] = pd2hv.pd2hv.compile(
                pd_path=in_path,
                hv_dir=os.path.join(out_dir, "hv"),
                search_paths=search_paths,
                verbose=verbose)
        elif in_path.endswith(".maxpat"):
            results["max2hv"] = max2hv.max2hv.compile(
                max_path=in_path,
                hv_dir=os.path.join(out_dir, "hv"),
                search_paths=search_paths,
                verbose=verbose)

        # check for errors
        if list(results.values())[0]["notifs"].get("has_error", False):
            return results

        results["hv2ir"] = hv2ir.hv2ir.compile(
            hv_file=os.path.join(list(results.values())[0]["out_dir"], list(results.values())[0]["out_file"]),
            # ensure that the ir filename has no funky characters in it
            ir_file=os.path.join(out_dir, "ir", re.sub("\W", "_", patch_name) + ".heavy.ir.json"),
            patch_name=patch_name,
            verbose=verbose)

        # check for errors
        if results["hv2ir"]["notifs"].get("has_error", False):
            return results

        # get the hvir data
        hvir = results["hv2ir"]["ir"]
        patch_name = hvir["name"]["escaped"]
        externs = generate_extern_info(hvir, results)

        c_src_dir = os.path.join(out_dir, "c")
        results["ir2c"] = ir2c.ir2c.compile(
            hv_ir_path=os.path.join(results["hv2ir"]["out_dir"], results["hv2ir"]["out_file"]),
            static_dir=os.path.join(os.path.dirname(__file__), "generators/ir2c/static"),
            output_dir=c_src_dir,
            externs=externs,
            copyright=copyright)

        # check for errors
        if results["ir2c"]["notifs"].get("has_error", False):
            return results

        # ir2c_perf
        results["ir2c_perf"] = {
            "stage": "ir2c_perf",
            "obj_counter": ir2c_perf.ir2c_perf.perf(results["hv2ir"]["ir"], verbose=verbose),
            "in_dir": results["hv2ir"]["out_dir"],
            "in_file": results["hv2ir"]["out_file"],
            "notifs": {}
        }

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
                        hvir = json.load(f)
                        patch_name = hvir["name"]["escaped"]
                        externs = generate_extern_info(hvir, results)
                else:
                    return add_error(results, "Cannot find hvir file.")
            except Exception as e:
                return add_error(results, f"ir could not be found or loaded: {e}.")

    # run the c2x generators, merge the results
    num_input_channels = hvir["signal"]["numInputBuffers"]
    num_output_channels = hvir["signal"]["numOutputBuffers"]

    if "bela" in generators:
        if verbose:
            print("--> Generating Bela plugin")
        results["c2bela"] = c2bela.c2bela.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "bela"),
            patch_name=patch_name,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            verbose=verbose)

    if "fabric" in generators:
        if verbose:
            print("--> Generating Fabric plugin")
        results["c2fabric"] = c2fabric.c2fabric.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "fabric"),
            patch_name=patch_name,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "js" in generators:
        if verbose:
            print("--> Generating Javascript")
        results["c2js"] = c2js.c2js.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "js"),
            patch_name=patch_name,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "daisy" in generators:
        if verbose:
            print("--> Generating Daisy module")
        results["c2daisy"] = c2daisy.c2daisy.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "daisy"),
            patch_name=patch_name,
            patch_meta=patch_meta,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "dpf" in generators:
        if verbose:
            print("--> Generating DPF plugin")
        results["c2dpf"] = c2dpf.c2dpf.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "plugin"),
            patch_name=patch_name,
            patch_meta=patch_meta,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "pdext" in generators:
        if verbose:
            print("--> Generating Pd external")
        results["c2pdext"] = c2pdext.c2pdext.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "pdext"),
            patch_name=patch_name,
            ext_name=patch_name + "~",
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "unity" in generators:
        if verbose:
            print("--> Generating Unity plugin")
        results["c2unity"] = c2unity.c2unity.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "unity"),
            patch_name=patch_name,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            copyright=copyright,
            verbose=verbose)

    if "wwise" in generators:
        if verbose:
            print("--> Generating Wwise plugin")
        results["c2wwise"] = c2wwise.c2wwise.compile(
            c_src_dir=c_src_dir,
            out_dir=os.path.join(out_dir, "wwise"),
            patch_name=patch_name,
            num_input_channels=num_input_channels,
            num_output_channels=num_output_channels,
            externs=externs,
            verbose=verbose)

    return results


def main():
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
        help="List of generator outputs: c, unity, wwise, js, pdext, daisy, dpf, fabric")
    parser.add_argument(
        "--results_path",
        help="Write results dictionary to the given path as a JSON-formatted string."
             " Target directory will be created if it does not exist.")
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
        verbose=args.verbose,
        copyright=args.copyright)

    for r in list(results.values()):
        # print any errors
        if r["notifs"].get("has_error", False):
            for i, error in enumerate(r["notifs"].get("errors", [])):
                print("{4:3d}) {2}Error{3} {0}: {1}".format(
                    r["stage"], error["message"], Colours.red, Colours.end, i + 1))

            # only print exception if no errors are indicated
            if len(r["notifs"].get("errors", [])) == 0 and r["notifs"].get("exception", None) is not None:
                print("{2}Error{3} {0} exception: {1}".format(
                    r["stage"], r["notifs"]["exception"], Colours.red, Colours.end))

            # clear any exceptions such that results can be JSONified if necessary
            r["notifs"]["exception"] = []

        # print any warnings
        for i, warning in enumerate(r["notifs"].get("warnings", [])):
            print("{4:3d}) {2}Warning{3} {0}: {1}".format(
                r["stage"], warning["message"], Colours.yellow, Colours.end, i + 1))

    if args.results_path:
        results_path = os.path.realpath(os.path.abspath(args.results_path))
        results_dir = os.path.dirname(results_path)

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        with open(results_path, "w") as f:
            json.dump(results, f)

    if args.verbose:
        print("Total compile time: {0:.2f}ms".format(1000 * (time.time() - tick)))


if __name__ == "__main__":
    main()
