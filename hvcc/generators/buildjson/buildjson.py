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

from collections import defaultdict
import json
import os

# generate build configuration files for use with https://github.com/enzienaudio/courtesan
# Example arguments:
#   macos_x64_args=["-project", "Hv_test_WwiseSourcePlugin.xcodeproj", "-arch", "x86_64", "-alltargets"]
#   android_armv7a_args=["APP_ABI=armeabi-v7a", "-j"]
#   win_x64_args=["/property:Configuration=Release", "/property:Platform=x64",
#                 "/t:Rebuild", "Hv_{0}_Unity.sln".format(patch_name), "/m"]


def generate_json(out_dir, android_armv7a_args=None, ios_armv7a_args=None,
                  linux_armv7a_args=None, linux_x64_args=None, macos_x64_args=None,
                  win_x64_args=None, win_x86_args=None):
    build_json = defaultdict(dict)

    if android_armv7a_args:
        build_json["android"]["armv7a"] = {
            "args": [android_armv7a_args],
            "projectDir": ["android", "jni"],
            "binaryDir": ["android", "libs", "armeabi-v7a"]
        }
    if ios_armv7a_args:
        build_json["ios"]["armv7a"] = {
            "args": [ios_armv7a_args],
            "projectDir": ["xcode"],
            "binaryDir": ["build", "ios", "armv7s", "Release"]
        }
    if linux_armv7a_args:
        build_json["linux"]["armv7a"] = {
            "args": [linux_armv7a_args],
            "projectDir": ["linux"],
            "binaryDir": ["build", "linux", "armv7a", "release"]
        }
    if linux_x64_args:
        build_json["linux"]["x64"] = {
            "args": [linux_x64_args],
            "projectDir": ["linux"],
            "binaryDir": ["build", "linux", "x64", "release"]
        }
    if macos_x64_args:
        build_json["macos"]["x64"] = {
            "args": [macos_x64_args],
            "projectDir": ["xcode"],
            "binaryDir": ["build", "macos", "x86_64", "Release"]
        }
    if win_x64_args:
        build_json["win"]["x64"] = {
            "args": [win_x64_args],
            "projectDir": ["vs2015"],
            "binaryDir": ["build", "win", "x64", "Release"]
        }
    if win_x86_args:
        build_json["win"]["x86"] = {
            "args": [win_x86_args],
            "projectDir": ["vs2015"],
            "binaryDir": ["build", "win", "x86", "Release"]
        }

    with open(os.path.join(out_dir, "build.json"), "w") as f:
        json.dump(build_json, f)
