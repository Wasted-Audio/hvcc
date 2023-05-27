# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2021-2023 Wasted Audio
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

import hashlib
import os


def filter_max(i: int, j: int) -> int:
    """Calculate the maximum of two integers.
    """
    return max(int(i), int(j))


def filter_plugin_id(s: str) -> int:
    """ Return a unique id from patch name
        [0...32767
    """
    sh = hashlib.md5(s.encode('utf-8'))
    sd = sh.hexdigest()[:4]
    return int(sd, 16) & 0x7FFF


def filter_string_cap(s: str, li: int) -> str:
    """Returns a truncated string with ellipsis if it exceeds a certain length.
    """
    return s if (len(s) <= li) else f"{s[0:li - 3]}..."


def filter_templates(template_name: str) -> bool:
    return False if os.path.basename(template_name) in [".DS_Store"] else True


def filter_uniqueid(s: str) -> str:
    """ Return a unique id (in hexadecimal) for the Plugin interface.
    """
    sh = hashlib.md5(s.encode('utf-8'))
    sd = sh.hexdigest().upper()[0:8]
    return f"0x{sd}"


def filter_xcode_build(s: str) -> str:
    """Return a build hash suitable for use in an Xcode project file.
    """
    s = f"{s}_build"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]


def filter_xcode_copy(s: str) -> str:
    """Return a copyref hash suitable for use in an Xcode project file.
    """
    s = f"{s}_copy"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]


def filter_xcode_fileref(s: str) -> str:
    """Return a fileref hash suitable for use in an Xcode project file.
    """
    s = f"{s}_fileref"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]
