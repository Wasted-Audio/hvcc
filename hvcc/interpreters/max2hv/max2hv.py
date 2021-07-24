# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

import argparse
import json
import os
import time

from .MaxParser import MaxParser


class max2hv:

    @classmethod
    def compile(clazz, max_path, hv_dir, search_paths=None, verbose=False):
        tick = time.time()

        max_graph = MaxParser.graph_from_file(max_path)

        if not os.path.exists(hv_dir):
            os.makedirs(hv_dir)

        hv_file = os.path.basename(max_path).split(".")[0] + ".hv.json"
        hv_path = os.path.join(hv_dir, hv_file)
        with open(hv_path, "w") as f:
            if verbose:
                f.write(json.dumps(
                    max_graph.to_hv(),
                    sort_keys=True,
                    indent=2,
                    separators=(",", ": ")))
            else:
                f.write(json.dumps(max_graph.to_hv()))

        return {
            "stage": "max2hv",
            "notifs": {
                "has_error": False,
                "exception": None,
                "errors": []
            },
            "in_dir": os.path.dirname(max_path),
            "in_file": os.path.basename(max_path),
            "out_dir": hv_dir,
            "out_file": hv_file,
            "compile_time": (time.time() - tick)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Converts a Max patch into the Heavy language format.")
    parser.add_argument(
        "max_path",
        help="The Max patch to convert to Heavy")
    parser.add_argument(
        "hv_dir",
        help="Directory to store generated Heavy patches.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show debugging information",
        action="count")
    args = parser.parse_args()

    args.max_path = os.path.abspath(os.path.expanduser(args.max_path))
    args.hv_dir = os.path.abspath(os.path.expanduser(args.hv_dir))

    result = max2hv.compile(
        max_path=args.max_path,
        hv_dir=args.hv_dir,
        search_paths=None,
        verbose=args.verbose)

    if result["notifs"].get("has_error", False):
        print(result["notifs"]["errors"])

    if args.verbose:
        print("Heavy file written to", os.path.join(result["output_dir"], result["output_file"]))
        print("Total max2hv compile time: {0:.2f}ms".format(result["compile_time"] * 1000))


if __name__ == "__main__":
    main()
