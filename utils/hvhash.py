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

import core.hv2ir.HeavyLangObject as HeavyLangObject

def main():
    parser = argparse.ArgumentParser(
        description="Prints the heavy hash of the input string.")
    parser.add_argument(
        "string",
        help="String to convert to hash.")
    args = parser.parse_args()

    print("0x{0:X}".format(HeavyLangObject.HeavyLangObject.get_hash(args.string)))

if __name__ == "__main__":
    main()
