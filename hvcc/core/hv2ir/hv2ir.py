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
import json
import os
import time

from .HeavyException import HeavyException
from .HeavyParser import HeavyParser


class hv2ir:

    @classmethod
    def compile(clazz, hv_file, ir_file, patch_name=None, verbose=False):
        """ Compiles a HeavyLang file into a HeavyIR file.
            Returns a tuple of compile time in seconds, a notification dictionary,
            and a heavy object counter.
        """

        # keep track of the total compile time
        tick = time.time()

        hv_file = os.path.abspath(os.path.expanduser(hv_file))
        ir_file = os.path.abspath(os.path.expanduser(ir_file))

        try:
            # parse heavy file
            hv_graph = HeavyParser.graph_from_file(hv_file=hv_file, xname=patch_name)
        except HeavyException as e:
            return {
                "stage": "hv2ir",
                "compile_time": time.time() - tick,
                "notifs": {
                    "has_error": True,
                    "exception": e,
                    "errors": [{"message": e.message}],
                    "warnings": []
                },
                "obj_counter": None,
                "in_file": os.path.basename(hv_file),
                "in_dir": os.path.dirname(hv_file),
                "out_file": os.path.basename(ir_file),
                "out_dir": os.path.dirname(ir_file)
            }

        try:
            # get a counter of all heavy objects
            hv_counter = hv_graph.get_object_counter(recursive=True)

            # prepare the graph for exporting
            hv_graph.prepare()

            # ensure that the output directory exists
            if not os.path.exists(os.path.dirname(ir_file)):
                os.makedirs(os.path.dirname(ir_file))

            # generate Heavy.IR
            ir = hv_graph.to_ir()
        except HeavyException as e:
            return {
                "stage": "hv2ir",
                "compile_time": time.time() - tick,
                "notifs": {
                    "has_error": True,
                    "exception": e,
                    "errors": [{"message": e.message}],
                    "warnings": []
                },
                "obj_counter": hv_counter,
                "in_file": os.path.basename(hv_file),
                "in_dir": os.path.dirname(hv_file),
                "out_file": os.path.basename(ir_file),
                "out_dir": os.path.dirname(ir_file)
            }

        # write the hv.ir file
        with open(ir_file, "w") as f:
            if verbose:
                json.dump(
                    ir,
                    f,
                    sort_keys=True,
                    indent=2,
                    separators=(",", ": "))
            else:
                json.dump(ir, f)

        if verbose:
            if len(ir["signal"]["processOrder"]) > 0:
                print("")
                print("=== Signal Order ===")
                for so in ir["signal"]["processOrder"]:
                    o = ir["objects"][so["id"]]
                    if len(o["args"]) > 0:
                        print("{0} {{{1}}}".format(
                            o["type"],
                            " ".join(["{0}:{1}".format(k, v) for k, v in o["args"].items()])))
                    else:
                        print(o["type"])

        return {
            "stage": "hv2ir",
            "compile_time": time.time() - tick,  # record the total compile time
            "notifs": hv_graph.get_notices(),
            "obj_counter": hv_counter,
            "in_file": os.path.basename(hv_file),
            "in_dir": os.path.dirname(hv_file),
            "out_file": os.path.basename(ir_file),
            "out_dir": os.path.dirname(ir_file),
            "ir": ir
        }


def main():
    parser = argparse.ArgumentParser(
        description="A C-language compiler for the Heavy audio programming language.")
    parser.add_argument(
        "hv_path",
        help="The patch to the top-level patch to compile.")
    parser.add_argument(
        "--hv_ir_path",
        default="./heavy.hv.ir.json",
        help="The output path of the hv.ir.json file.")
    parser.add_argument(
        "--name",
        default="heavy",
        help="")
    parser.add_argument("-v", "--verbose", action="count")
    args = parser.parse_args()

    d = hv2ir.compile(
        hv_file=args.hv_path,
        ir_file=args.hv_ir_path,
        patch_name=args.name,
        verbose=args.verbose)

    if args.verbose:
        print("Total hv2ir time: {0:.2f}ms".format(d["compile_time"] * 1000))


if __name__ == "__main__":
    main()
