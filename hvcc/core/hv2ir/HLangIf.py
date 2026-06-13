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

# from pathlib import Path

# from .HeavyException import HeavyException
# from .HeavyIrObject import HeavyIrObject
# from .HeavyLangObject import HeavyLangObject

# class HLangIf(HeavyLangObject):
#     """ Translates HeavyLang object [if] to HeavyIR [if] or [if~].
#     """

#     def __init__(
#         self,
#         obj_type: str,
#         args: Dict,
#         graph: HeavyGraph,
#         annotations: Optional[Dict] = None
#     ) -> None:
#         assert obj_type == "if"
#         super().__init__("if", args, graph, num_inlets=2, num_outlets=2, annotations=annotations)

#     def reduce(self) -> Tuple[Set, List]:
#         if self.has_inlet_connection_format(["cc", "_c", "c_", "__"]):
#             x = HeavyIrObject("__if", self.args)
#         elif self.has_inlet_connection_format("ff"):
#             # TODO(mhroth): implement this
#             x = HeavyParser.graph_from_file(Path("./hvlib/if~f.hv.json"))
#         elif self.has_inlet_connection_format("ii"):
#             # TODO(mhroth): implement this
#             x = HeavyParser.graph_from_file(Path("./hvlib/if~i.hv.json"))
#         else:
#             fmt = self._get_connection_format(self.inlet_connections)
#             raise HeavyException(f"Unhandled connection configuration to object [if]: {fmt}")

#         return ({x}, self.get_connection_move_list(x))
