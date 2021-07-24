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

import os


class PrettyfyC:

    @classmethod
    def prettyfy_file(clazz, file_in, file_out, indent=0, step=2, delete_input_on_finish=False):
        with open(file_in, "r") as f:
            with open(file_out, "w") as g:
                for line in f:
                    indent -= line.count("}")
                    new_line = (" " * (step * indent)) + line
                    g.write(new_line + os.linesep)
                    indent += line.count("{")

        if delete_input_on_finish:
            os.path.delete(file_in)

    @classmethod
    def prettyfy_list(clazz, list_in, indent=0, step=2):
        g = []
        for line in list_in:
            indent -= line.count("}")
            new_line = (" " * (step * indent)) + line
            g.append(new_line)
            indent += line.count("{")
        return g
