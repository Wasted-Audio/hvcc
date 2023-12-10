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

import json
import random
import os

from typing import Any, Dict, Optional

from .HIrConvolution import HIrConvolution
from .HIrInlet import HIrInlet
from .HIrLorenz import HIrLorenz
from .HIrOutlet import HIrOutlet
from .HIrPack import HIrPack
from .HIrSwitchcase import HIrSwitchcase
from .HIrTabhead import HIrTabhead
from .HIrTabread import HIrTabread
from .HIrTabwrite import HIrTabwrite

from .HLangAdc import HLangAdc
from .HLangBinop import HLangBinop
from .HLangBiquad import HLangBiquad
from .HLangDac import HLangDac
from .HLangDelay import HLangDelay
# from .HLangIf import HLangIf  # circular import. moved here
from .HeavyException import HeavyException
from .HeavyIrObject import HeavyIrObject
from .HeavyLangObject import HeavyLangObject
from .HLangLine import HLangLine
from .HLangMessage import HLangMessage
# from .HLangNoise import HLangNoise  # circular import. moved here
from .HLangPhasor import HLangPhasor
from .HLangPrint import HLangPrint
from .HLangReceive import HLangReceive
from .HLangRandom import HLangRandom
from .HLangSend import HLangSend
from .HLangSequence import HLangSequence
from .HLangSlice import HLangSlice
from .HLangSystem import HLangSystem
from .HLangTable import HLangTable
from .HLangUnop import HLangUnop
from .HLangVar import HLangVar
from .HLangVario import HLangVario

from .HeavyGraph import HeavyGraph
from .Connection import Connection


class HeavyParser:

    @classmethod
    def graph_from_file(
        cls,
        hv_file: str,
        graph: Optional[HeavyGraph] = None,
        graph_args: Optional[Dict] = None,
        path_stack: Optional[set] = None,
        xname: Optional[str] = None
    ) -> HeavyGraph:
        """ Read a graph object from a file.

            @param graph  The parent graph of this graph.
            @param graph_args  The arguments to this graph, in the form of a completely
            resolved dictionary.
            @param path_stack  The path_stack is the current stack of resolved abstractions.
            It prevents infinite recursion when reading many abstractions deep.
        """
        # ensure that we have an absolute path to the hv_file
        hv_file = os.path.abspath(os.path.expanduser(hv_file))

        # copy the path stack such that no changes are made to the calling stack
        path_stack = path_stack or set()
        if hv_file in path_stack:
            raise HeavyException(f"Abstraction recursion detected. Rereading {hv_file} on stack {path_stack}.")
        else:
            path_stack.add(hv_file)

        # open and parse the heavy file
        with open(hv_file, "r") as f:
            json_heavy = json.load(f)

        return cls.graph_from_object(hv_file, json_heavy, path_stack, graph, graph_args, xname)

    @classmethod
    def graph_from_object(
        cls,
        hv_file: str,
        json_heavy: Dict,
        path_stack: set,
        graph: Optional[HeavyGraph] = None,
        graph_args: Optional[Dict] = None,
        xname: Optional[str] = None
    ) -> HeavyGraph:

        """ Parse a graph object.

            @param graph  The parent graph.
            @param graph_args  The resolved arguments to this graph, in the form of a dictionary.
            @param hv_file  The Heavy file where this graph can be found.
        """
        # resolve default graph arguments
        graph_args = graph_args or {}
        for a in json_heavy["args"]:
            if a["name"] not in graph_args:
                if a["required"]:
                    raise HeavyException(f"Required argument \"{a['name']}\" not present.")
                else:
                    graph_args[a["name"]] = a["default"]
            else:
                # just to be safe, ensure that the argument type is correct
                graph_args[a["name"]] = HeavyLangObject.force_arg_type(
                    graph_args[a["name"]],
                    a["value_type"],
                    graph=graph)

        # create a new graph
        subpatch_name = json_heavy.get("annotations", {}).get("name", xname)
        g = HeavyGraph(graph, graph_args, file=hv_file, xname=subpatch_name)

        # add the import paths to the global vars
        g.local_vars.add_import_paths(json_heavy.get("imports", []))
        # add the file's relative directory to global vars
        g.local_vars.add_import_paths([os.path.dirname(hv_file)])

        # instantiate all objects
        try:
            for obj_id, o in json_heavy["objects"].items():
                if o["type"] == "comment":
                    continue  # first and foremost, ignore comment objects

                elif o["type"] == "graph":
                    # inline HeavyGraph objects (i.e. subgraphs)
                    # require a different set of initialisation arguments
                    x: Any = cls.graph_from_object(hv_file, o, path_stack, g, g.args, xname)

                else:
                    # resolve the arguments dictionary based on the graph args
                    args = g.resolve_arguments(o["args"])

                    # before anything, search for an abstraction
                    # in case we want to override default functionality
                    # However, if we are in an abstraction that has the same
                    # name as the type that we are looking for, don't recurse!
                    abs_path = g.find_path_for_abstraction(o["type"])
                    if abs_path is not None and abs_path not in path_stack:
                        x = cls.graph_from_file(
                            hv_file=abs_path,
                            graph=g,
                            graph_args=args,
                            path_stack=path_stack)

                    # if we know how to handle this object type natively
                    # either as a custom type or as a generic IR object
                    elif HeavyParser.get_class_for_type(o["type"]) is not None:
                        obj_cls = HeavyParser.get_class_for_type(o["type"])
                        x = obj_cls(o["type"], args, g, o.get("annotations", {}))

                    # handle generic IR objects
                    elif HeavyIrObject.is_ir(o["type"]):
                        x = HeavyIrObject(o["type"], args, g, annotations=o.get("annotations", {}))

                    # an object definition can't be found
                    else:
                        g.add_error(f"Object type \"{o['type']}\" cannot be found.")
                        # note that add_error() raises an exception. So really, there is no continue.
                        continue

                # add the new object to the graph's object dictionary
                g.add_object(x, obj_id)

            # parse all of the connections
            for c in json_heavy["connections"]:
                g.connect_objects(Connection(
                    g.objs[c["from"]["id"]],
                    c["from"]["outlet"],
                    g.objs[c["to"]["id"]],
                    c["to"]["inlet"],
                    c["type"]))

        except HeavyException as e:
            if g.is_root_graph():
                # add the notification dictionary at the top level
                e.notes = g.get_notices()
                e.notes["has_error"] = True
                e.notes["exception"] = e
            raise e

        if (g.graph is None) or (g.graph.file != g.file):
            # remove this graph from the stack when finished.
            # Subpatches should not remove themselves.
            path_stack.remove(g.file)

        return g

    @classmethod
    def get_class_for_type(cls, obj_type: str) -> Any:
        """ Returns the class which can handle the given object type.
        """
        if HLangUnop.handles_type(obj_type):
            return HLangUnop
        elif HLangBinop.handles_type(obj_type):
            return HLangBinop
        elif obj_type in LANG_CLASS_DICT:
            return LANG_CLASS_DICT[obj_type]
        else:
            return None


class HLangIf(HeavyLangObject):
    """ Translates HeavyLang object [if] to HeavyIR [if] or [if~].
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: HeavyGraph,
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "if"
        super().__init__("if", args, graph, num_inlets=2, num_outlets=2, annotations=annotations)

    def reduce(self) -> tuple:
        if self.has_inlet_connection_format(["cc", "_c", "c_", "__"]):
            x = HeavyIrObject("__if", self.args)
        elif self.has_inlet_connection_format("ff"):
            # TODO(mhroth): implement this
            x = HeavyParser.graph_from_file("./hvlib/if~f.hv.json")
        elif self.has_inlet_connection_format("ii"):
            # TODO(mhroth): implement this
            x = HeavyParser.graph_from_file("./hvlib/if~i.hv.json")
        else:
            fmt = self._get_connection_format(self.inlet_connections)
            raise HeavyException(f"Unhandled connection configuration to object [if]: {fmt}")

        return ({x}, self.get_connection_move_list(x))


class HLangNoise(HeavyLangObject):
    """ Handles the HeavyLang "noise" object.
    """

    def __init__(
        self,
        obj_type: str,
        args: Dict,
        graph: HeavyGraph,
        annotations: Optional[Dict] = None
    ) -> None:
        assert obj_type == "noise"
        super().__init__("noise", args, graph, num_inlets=1, num_outlets=1, annotations=annotations)

    def reduce(self) -> tuple:
        seed = int(random.uniform(1, 2147483647))  # assign a random 32-bit seed
        noise_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./hvlib/noise.hv.json")
        x = HeavyParser.graph_from_file(noise_path, graph_args={"seed": seed})
        x.reduce()
        # TODO(mhroth): deal with control input
        return ({x}, self.get_connection_move_list(x))


# A list of all of the HeavyLang objects and the classes
# that will translate them into HeavyIR objects.
LANG_CLASS_DICT = {
    "__conv~f": HIrConvolution,
    "biquad": HLangBiquad,
    "if": HLangIf,
    "inlet": HIrInlet,
    "var": HLangVar,
    "vario": HLangVario,
    "outlet": HIrOutlet,
    "__lorenz~f": HIrLorenz,
    "print": HLangPrint,
    "sequence": HLangSequence,
    "adc": HLangAdc,
    "dac": HLangDac,
    "message": HLangMessage,
    "noise": HLangNoise,
    "system": HLangSystem,
    "phasor": HLangPhasor,
    "line": HLangLine,
    "random": HLangRandom,
    "delay": HLangDelay,
    "table": HLangTable,
    "slice": HLangSlice,
    "__tabread~if": HIrTabread,
    "__tabread~f": HIrTabread,
    "__tabread_stoppable~f": HIrTabread,
    "__tabreadu~f": HIrTabread,
    "__tabread": HIrTabread,
    "__tabhead~f": HIrTabhead,
    "__tabhead": HIrTabhead,
    "__tabwrite~f": HIrTabwrite,
    "__tabwrite_stoppable~f": HIrTabwrite,
    "__tabwrite": HIrTabwrite,
    "receive": HLangReceive,
    "send": HLangSend,
    "__switchcase": HIrSwitchcase,
    "switchcase": HIrSwitchcase,
    "__pack": HIrPack
}
