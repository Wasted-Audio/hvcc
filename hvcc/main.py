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
import json
import os
import sys
import time

from hvcc.version import VERSION
from hvcc.compiler import compile_dataflow


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


def main() -> bool:
    tick = time.time()

    parser = argparse.ArgumentParser(
        description="This is the Wasted Audio Heavy compiler. It compiles supported dataflow languages into C,"
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
    parser.add_argument(
        "-V",
        "--version",
        action='version',
        help="Print version and exit.",
        version=VERSION
    )
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
    for r in list(results.root.values()):
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
            json.dump(results.model_dump(), f)

    if args.verbose:
        print("Total compile time: {0:.2f}ms".format(1000 * (time.time() - tick)))
    return errorCount != 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
