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

import sys
import argparse
import json

import hvcc.core.hv2ir.HeavyLangObject as HeavyLangObject
import hvcc.interpreters.pd2hv.PdParser as PdParser


def main():
    parser = argparse.ArgumentParser(
        description="Some separate heavy utilities, wrapped into a single app")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("pdobjects", help="list supported Pure Data objects")
    subparser_hvhash = subparsers.add_parser("hvhash", help="print the heavy hash of the input string")
    subparser_hvhash.add_argument("string")

    parsed_args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    args = vars(parsed_args)

    command = args.pop("command")
    if command == "pdobjects":
        obj_list = PdParser.PdParser.get_supported_objects()
        print(json.dumps(obj_list, indent=4))
    elif command == "hvhash":
        print("0x{0:X}".format(HeavyLangObject.HeavyLangObject.get_hash(args.get('string'))))
    else:
        pass


if __name__ == "__main__":
    main()
