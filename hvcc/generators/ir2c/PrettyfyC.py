# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023 Wasted Audio
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
from typing import List


class PrettyfyC:

    @classmethod
    def prettyfy_file(
        cls,
        file_in: str,
        file_out: str,
        indent: int = 0,
        step: int = 2,
        delete_input_on_finish: bool = False
    ) -> None:
        with open(file_in, "r") as f:
            with open(file_out, "w") as g:
                for line in f:
                    indent -= line.count("}")
                    new_line = (" " * (step * indent)) + line
                    g.write(new_line + os.linesep)
                    indent += line.count("{")

        if delete_input_on_finish:
            os.remove(file_in)

    @classmethod
    def prettyfy_list(
        cls,
        list_in: List,
        indent: int = 0,
        step: int = 2
    ) -> List:
        g = []
        for line in list_in:
            indent -= line.count("}")
            new_line = (" " * (step * indent)) + line
            g.append(new_line)
            indent += line.count("{")
        return g
