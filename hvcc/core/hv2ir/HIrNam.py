# Copyright (C) 2026 Wasted Audio
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

from typing import Dict, Optional
from pathlib import Path

from .HeavyIrObject import HeavyIrObject
from .HeavyGraph import HeavyGraph

from hvcc.generators.ir2c.SignalNamHeader import ModelNet, load_nam_file


class HIrNam(HeavyIrObject):
    """ __nam~f
    """

    def __init__(
        self,
        obj_type: str,
        args: Optional[Dict] = None,
        graph: Optional[HeavyGraph] = None,
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "__nam~f"

        # load the nam file to retrieve the model type
        assert args is not None
        model_net, _, _ = load_nam_file(Path(args["nam"]))

        # overload the object type based on the model
        if model_net == ModelNet.Nano:
            obj_type = "__nam_nano~f"
        elif model_net == ModelNet.Feather:
            obj_type = "__nam_feather~f"
        elif model_net == ModelNet.Lite:
            obj_type = "__nam_lite~f"
        elif model_net == ModelNet.Standard:
            obj_type = "__nam_standard~f"

        super().__init__(obj_type, args=args, graph=graph, annotations=annotations)
