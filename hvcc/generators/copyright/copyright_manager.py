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

import datetime
import os


def get_default_copyright_text():
    with open(os.path.join(os.path.dirname(__file__), "default_template.txt"), "r") as f:
        copyright = f.read().format(datetime.datetime.now().year)
    return copyright


def get_copyright_for_c(copyright_text=None):
    """ Returns an input string as a C-formatted comment, otherwise a default
        copyright statement if the input is None.
    """
    return comment_for_c(copyright_text or get_default_copyright_text())


def get_copyright_for_xml(copyright_text=None):
    """ Returns an input string as an xml comment, otherwise a default
        copyright statement if the input is None.
    """
    return comment_for_xml(copyright_text or get_default_copyright_text())


def comment_for_c(comment):
    """ Returns the input string as a C-formatted comment, suitable for copyright statements.
    """
    if "\n" in comment:
        return "/**\n * {0}\n */".format("\n * ".join(comment.split("\n")))
    else:
        return "/** {0} */".format(comment)


def comment_for_xml(comment):
    """ Returns the input string as a XML comment, suitable for copyright statements.
    """
    if "\n" in comment:
        return "<!--\n{0}\n-->".format(comment)
    else:
        return "<!-- {0} -->".format(comment)
