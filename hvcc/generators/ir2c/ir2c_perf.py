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
from collections import Counter
from collections import defaultdict
import json
import os


class ir2c_perf:

    @classmethod
    def perf(clazz, ir, blocksize=512, mhz=1000, verbose=False):
        # read the hv.ir.json file
        with open(os.path.join(os.path.dirname(__file__), "../../core/json/heavy.ir.json"), "r") as f:
            HEAVY_IR_JSON = json.load(f)

        objects = Counter()
        perf = Counter()
        per_object_perf = defaultdict(Counter)
        for o in ir["signal"]["processOrder"]:
            obj_id = o["id"]
            obj_type = ir["objects"][obj_id]["type"]
            if obj_type in HEAVY_IR_JSON:
                objects[obj_type] += 1
                if "perf" in HEAVY_IR_JSON[obj_type]:
                    c = Counter(HEAVY_IR_JSON[obj_type]["perf"])
                    perf = perf + c
                    per_object_perf[obj_type] = per_object_perf[obj_type] + c
                else:
                    print("{0} requires perf information.".format(obj_type))
            else:
                print("ERROR: Unknown object type {0}".format(obj_type))

        if verbose:
            print("AVX: {0} cycles / {1} cycles per frame".format(perf["avx"], perf["avx"] / 8.0))
            print("     {0} frames @ {1}MHz >= {2:.2f}us".format(
                blocksize,
                mhz,
                blocksize * perf["avx"] / 8.0 / mhz))

            print  # new line

            print("SSE: {0} cycles / {1} cycles per frame".format(perf["sse"], perf["sse"] / 4.0))
            print("     {0} frames @ {1}MHz >= {2:.2f}us".format(
                blocksize,
                mhz,
                blocksize * perf["sse"] / 4.0 / mhz))

            print  # new line

            print("{0:<4} {1:<5} {2:<16} {3}".format("CPU%", "#Objs", "Object Type", "Performance"))
            print("==== ===== ================ ===========")

            # print object in order of highest load
            items = per_object_perf.items()
            # items.sort(key=lambda o: o[1]["avx"], reverse=True)
            for k, v in items:
                print("{2:>2.2g}%  {3:<5} {0:<16} {1}".format(k, v, int(100.0 * v["avx"] / perf["avx"]), objects[k]))

        return per_object_perf


def main():
    parser = argparse.ArgumentParser(
        description="A Heavy.IR to C-language translator.")
    parser.add_argument(
        "hv_ir_path",
        help="The path to the Heavy.IR file to read.")
    parser.add_argument("--mhz", default=1000, type=float, help="the CPU clock frequency in MHz")
    parser.add_argument("--blocksize", default=64, type=int, help="the number of frames per block")
    parser.add_argument("-v", "--verbose", action="count")
    args = parser.parse_args()

    # read the hv.ir.json file
    with open(args.hv_ir_path, "r") as f:
        ir = json.load(f)

    ir2c_perf.perf(ir, args.blocksize, args.mhz, args.verbose)


if __name__ == "__main__":
    main()
