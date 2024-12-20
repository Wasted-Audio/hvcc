# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023-2024 Wasted Audio
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

from collections import Counter, defaultdict
from typing import Dict

from hvcc.types.IR import HeavyIRType, IRGraph


class ir2c_perf:

    @classmethod
    def perf(
        cls,
        ir: IRGraph,
        blocksize: int = 512,
        mhz: int = 1000,
        verbose: bool = False
    ) -> Dict[str, Counter]:
        # read the hv.ir.json file
        with open(os.path.join(os.path.dirname(__file__), "../../core/json/heavy.ir.json"), "r") as f:
            HEAVY_IR_JSON = HeavyIRType(**json.load(f)).root

        objects: Counter = Counter()
        perf: Counter = Counter()
        per_object_perf: Dict[str, Counter] = defaultdict(Counter)
        for o in ir.signal.processOrder:
            obj_id = o.id
            obj_type = ir.objects[obj_id].type
            if obj_type in HEAVY_IR_JSON.keys():
                objects[obj_type] += 1
                obj_perf = HEAVY_IR_JSON[obj_type].perf
                assert obj_perf is not None
                c = Counter(obj_perf.model_dump())
                perf = perf + c
                per_object_perf[obj_type] = per_object_perf[obj_type] + c
            else:
                print(f"ERROR: Unknown object type {obj_type}")

        if verbose:
            print("AVX: {0} cycles / {1} cycles per frame".format(perf["avx"], perf["avx"] / 8.0))
            print("     {0} frames @ {1}MHz >= {2:.2f}us".format(
                blocksize,
                mhz,
                blocksize * perf["avx"] / 8.0 / mhz))

            print()  # new line

            print("SSE: {0} cycles / {1} cycles per frame".format(perf["sse"], perf["sse"] / 4.0))
            print("     {0} frames @ {1}MHz >= {2:.2f}us".format(
                blocksize,
                mhz,
                blocksize * perf["sse"] / 4.0 / mhz))

            print()  # new line

            print("NEON: {0} cycles / {1} cycles per frame".format(perf["neon"], perf["neon"] / 4.0))
            print("     {0} frames @ {1}MHz >= {2:.2f}us".format(
                blocksize,
                mhz,
                blocksize * perf["neon"] / 4.0 / mhz))

            print()  # new line

            print("{0:<4} {1:<5} {2:<16} {3}".format("CPU%", "#Objs", "Object Type", "Performance"))
            print("==== ===== ================ ===========")

            # print object in order of highest load
            items = per_object_perf.items()
            # items.sort(key=lambda o: o[1]["avx"], reverse=True)
            for k, v in items:
                if perf["avx"] > 0:
                    print(
                        "{2:>2.2g}%  {3:<5} {0:<16} {1}".format(k, v, int(100.0 * v["avx"] / perf["avx"]), objects[k])
                    )

        return per_object_perf


def main() -> None:
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
