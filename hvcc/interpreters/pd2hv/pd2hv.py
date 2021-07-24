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

from .PdParser import PdParser


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


class pd2hv:

    @classmethod
    def get_supported_objects(clazz):
        return PdParser.get_supported_objects()

    @classmethod
    def compile(clazz, pd_path, hv_dir, search_paths=None, verbose=False, export_args=False):
        tick = time.time()

        parser = PdParser()  # create parser state
        if search_paths is not None:
            for p in search_paths:
                parser.add_absolute_search_directory(p)

        pd_graph = parser.graph_from_file(pd_path)
        notices = pd_graph.get_notices()

        # check for errors
        if len(notices["errors"]) > 0:
            return {
                "stage": "pd2hv",
                "obj_counter": dict(parser.obj_counter),
                "notifs": {
                    "has_error": True,
                    "exception": None,
                    "errors": notices["errors"],
                    "warnings": notices["warnings"]
                },
                "in_dir": os.path.dirname(pd_path),
                "in_file": os.path.basename(pd_path),
                "out_dir": None,
                "out_file": None,
                "compile_time": (time.time() - tick)
            }

        if not os.path.exists(hv_dir):
            os.makedirs(hv_dir)

        hv_file = os.path.splitext(os.path.basename(pd_path))[0] + ".hv.json"
        hv_path = os.path.join(hv_dir, hv_file)
        with open(hv_path, "w") as f:
            if verbose:
                json.dump(pd_graph.to_hv(export_args=export_args),
                          f,
                          sort_keys=True,
                          indent=2,
                          separators=(",", ": "))
            else:
                json.dump(pd_graph.to_hv(export_args=export_args), f)

        return {
            "stage": "pd2hv",
            "obj_counter": dict(parser.obj_counter),
            "notifs": {
                "has_error": False,
                "exception": None,
                "errors": notices["errors"],
                "warnings": notices["warnings"]
            },
            "in_dir": os.path.dirname(pd_path),
            "in_file": os.path.basename(pd_path),
            "out_dir": hv_dir,
            "out_file": hv_file,
            "compile_time": (time.time() - tick)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Converts a Pd patch into the Heavy language format.")
    parser.add_argument(
        "pd_path",
        help="The Pd patch to convert to Heavy.")
    parser.add_argument(
        "hv_dir",
        help="Directory to store generated Heavy patches.")
    parser.add_argument(
        "--export",
        help="Export Heavy arguments. Use this to make precompiled patches.",
        action="count")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show debugging information.",
        action="count")
    args = parser.parse_args()

    args.pd_path = os.path.abspath(os.path.expanduser(args.pd_path))
    args.hv_dir = os.path.abspath(os.path.expanduser(args.hv_dir))

    result = pd2hv.compile(
        pd_path=args.pd_path,
        hv_dir=args.hv_dir,
        search_paths=None,
        verbose=args.verbose,
        export_args=args.export)

    for i, n in enumerate(result["notifs"]["errors"]):
        print("{0:3d}) {1}Error #{2:4d}:{3} {4}".format(
            i + 1,
            Colours.red,
            n["enum"],
            Colours.end,
            n["message"]))
    for i, n in enumerate(result["notifs"]["warnings"]):
        print("{0:3d}) {1}Warning #{2:4d}:{3} {4}".format(
            i + 1,
            Colours.yellow,
            n["enum"],
            Colours.end,
            n["message"]))

    if args.verbose:
        if len(result["notifs"]["errors"]) == 0:
            print("Heavy file written to", os.path.join(result["out_dir"], result["out_file"]))
        print("Total pd2hv compile time: {0:.2f}ms".format(result["compile_time"] * 1000))


if __name__ == "__main__":
    main()
