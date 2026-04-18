# Copyright (C) 2014-2018 Enzien Audio, Ltd.
# Copyright (C) 2023-2026 Wasted Audio
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


# moved to HeavyParser.py because of circular dependency

# import random
# from pathlib import Path

# from .HeavyLangObject import HeavyLangObject
# from .HeavyParser import HeavyParser


# class HLangNoise(HeavyLangObject):
#     """ Handles the HeavyLang "noise" object.
#     """

#     def __init__(
#         self,
#         obj_type: str,
#         args: Dict,
#         graph: HeavyGraph,
#         annotations: Optional[Dict] = None
#     ) -> None:
#         assert obj_type == "noise"
#         super().__init__("noise", args, graph, num_inlets=1, num_outlets=1, annotations=annotations)

#     def reduce(self) -> Tuple[Set, List]:
#         seed = int(random.uniform(1, 2147483647))  # assign a random 32-bit seed
#         noise_path = Path(Path(__file__).parent, "./hvlib/noise.hv.json")
#         x = HeavyParser.graph_from_file(noise_path, graph_args={"seed": seed})
#         x.reduce()
#         # TODO(mhroth): deal with control input
#         return ({x}, self.get_connection_move_list(x))
