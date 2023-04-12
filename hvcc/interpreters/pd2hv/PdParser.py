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

import decimal
import os
import re
from collections import Counter
from collections import OrderedDict
from typing import List, Dict, Optional, Type, Any, Generator

from .HeavyObject import HeavyObject
from .HeavyGraph import HeavyGraph              # pre-converted Heavy graphs
from .HvSwitchcase import HvSwitchcase          # __switchcase
from .PdAudioIoObject import PdAudioIoObject    # adc~/dac~
from .PdBinopObject import PdBinopObject        # binary arithmatic operators
from .PdGraph import PdGraph                    # canvas
from .PdLetObject import PdLetObject            # inlet/inlet~/outlet/outlet~
from .PdMessageObject import PdMessageObject    # msg
from .PdPackObject import PdPackObject          # pack
from .PdReceiveObject import PdReceiveObject    # r/r~/receive/receive~/catch~
from .PdRouteObject import PdRouteObject        # route
from .PdSelectObject import PdSelectObject      # select/sel
from .PdSendObject import PdSendObject          # s/s~/send/send~/throw~
from .PdTriggerObject import PdTriggerObject    # trigger/t
from .PdTableObject import PdTableObject        # table
from .PdUnpackObject import PdUnpackObject      # unpack
from .PdLibSignalGraph import PdLibSignalGraph  # pd/lib abstraction connection checks

from .NotificationEnum import NotificationEnum


class PdParser:

    # library search paths
    __HVLIB_DIR = os.path.join(os.path.dirname(__file__), "libs", "heavy")
    __HVLIB_CONVERTED_DIR = os.path.join(os.path.dirname(__file__), "libs", "heavy_converted")
    __PDLIB_DIR = os.path.join(os.path.dirname(__file__), "libs", "pd")
    __PDLIB_CONVERTED_DIR = os.path.join(os.path.dirname(__file__), "libs", "pd_converted")

    # detect a dollar argument in a string
    __RE_DOLLAR = re.compile(r"\$(\d+)")

    # detect width parameter e.g. "#X obj 172 79 t b b, f 22;"
    __RE_WIDTH = re.compile(r", f \d+$")

    def __init__(self) -> None:
        # the current global value of $0
        # Note(joe): set a high starting value to avoid potential user naming conflicts
        self.__DOLLAR_ZERO = 1000

        # a counter of all Pd objects in the graph
        self.obj_counter: Counter = Counter()

        # search paths at this graph level
        self.__search_paths: List = []

    @classmethod
    def get_supported_objects(cls) -> List:
        """ Returns a set of all pd objects names supported by the parser.
        """
        pd_objects = [os.path.splitext(f)[0] for f in os.listdir(cls.__PDLIB_DIR) if f.endswith(".pd")]
        pd_objects.extend(cls.__PD_CLASSES.keys())
        return pd_objects

    @classmethod
    def __get_hv_args(cls, pd_path: str) -> OrderedDict:
        """ Pre-parse the file for Heavy arguments, such that they are available
            as soon as a graph is created.
        """
        num_canvas = -1
        hv_arg_dict = OrderedDict()
        hv_arg_list: Optional[List] = None
        with open(pd_path, "r") as f:
            for li in f:
                if li.startswith("#N canvas"):
                    hv_arg_list = []
                    hv_arg_dict[li.rstrip(";\r\n")] = hv_arg_list
                    num_canvas += 1
                elif "@hv_arg" in li and hv_arg_list is not None:
                    hv_arg_list.append(li.rstrip(";\r\n"))
                elif li.startswith("#X restore"):
                    num_canvas -= 1
                    hv_arg_list = list(hv_arg_dict.values())[num_canvas]
        return hv_arg_dict

    @classmethod
    def __get_pd_line(cls, pd_path: str) -> Generator:
        concat = ""  # concatination state
        with open(pd_path, "r") as f:
            for li in f:
                # concatenate split lines in the Pd file here
                li = li.rstrip("\r\n")  # account for windows CRLF
                if li.endswith(";") and not li.endswith(r"\;"):
                    out = li[:-1]  # remove single ";"
                    if len(concat) > 0:
                        out = f'{concat} {out}'
                        concat = ""  # reset concatenation state
                    yield out
                else:
                    concat = (f'{concat} {li}') if len(concat) > 0 else f'{li}'

    def add_absolute_search_directory(self, search_dir: str) -> bool:
        if os.path.isdir(search_dir):
            self.__search_paths.append(search_dir)
            return True
        else:
            return False

    def add_relative_search_directory(self, search_dir: str) -> bool:
        search_dir = os.path.abspath(os.path.join(
            self.__search_paths[0],
            search_dir))
        return self.add_absolute_search_directory(search_dir)

    def find_abstraction_path(self, local_dir: str, abs_name: str) -> Optional[str]:
        """ Finds the full path for an abstraction.
            Checks the local directory first, then all declared paths.
        """

        abs_filename = f'{abs_name}.pd'

        # check local directory first
        abs_path = os.path.join(os.path.abspath(local_dir), abs_filename)
        if os.path.isfile(abs_path):
            return abs_path

        # check search paths in reverse order (last added search path first)
        for d in reversed(self.__search_paths):
            abs_path = os.path.join(d, abs_filename)
            if os.path.isfile(abs_path):
                return abs_path

        return None

    def graph_from_file(
        self,
        file_path: str,
        obj_args: Optional[List] = None,
        pos_x: int = 0,
        pos_y: int = 0,
        is_root: bool = True,
        pd_graph_class: Type[PdGraph] = PdGraph
    ) -> Any:
        """ Instantiate a PdGraph from a file.
            Note that obj_args does not include $0.
            @param pd_graph_class  The python class to handle specific graph types
        """
        # add main patch directory. The first entry of self.__search_paths is
        # assumed to be the root path of the whole system

        if is_root:
            self.__search_paths.append(os.path.dirname(file_path))

        file_hv_arg_dict = self.__get_hv_args(file_path)
        file_iterator = self.__get_pd_line(file_path)
        canvas_line = file_iterator.__next__()

        self.__DOLLAR_ZERO += 1  # increment $0
        graph_args = [self.__DOLLAR_ZERO] + (obj_args or [])

        if not canvas_line.startswith("#N canvas"):
            g = pd_graph_class(graph_args, file_path, pos_x, pos_y)
            g.add_error(f"Pd files must begin with \"#N canvas\": {canvas_line}")
            return g

        g = self.graph_from_canvas(
            file_iterator,
            file_hv_arg_dict,
            canvas_line,
            graph_args,
            file_path,
            pos_x, pos_y,
            is_root,
            pd_graph_class)

        if is_root:
            if g.get_notices()["errors"]:
                # return the graph early here as there are already errors and it is
                # clearly invalid, avoids triggering unrelated errors in validation
                return g
            g.validate_configuration()

        return g

    def graph_from_canvas(
        self,
        file_iterator: Generator,
        file_hv_arg_dict: Dict,
        canvas_line: str,
        graph_args: List,
        pd_path: str,
        pos_x: int = 0,
        pos_y: int = 0,
        is_root: bool = False,
        pd_graph_class: Type[PdGraph] = PdGraph
    ) -> Any:
        """ Instantiate a PdGraph from an existing canvas.
            Note that graph_args includes $0.
            @param file_hv_arg_dict  A dictionary containing all Heavy argument lines
            for each "#N canvas" in this file.
            @param canvas_line  The "#N canvas" which initiates this canvas.
            @param pd_graph_class  The python class to handle specific graph types
        """
        obj_array: Optional[HeavyObject] = None  # an #A (table) object which is currently being parsed

        g = pd_graph_class(graph_args, pd_path, pos_x, pos_y)

        # parse and add all Heavy arguments to the graph
        for li in file_hv_arg_dict[canvas_line]:
            line = li.split()
            assert line[4] == "@hv_arg"
            is_required = (line[9] == "true")
            default_value = HeavyObject.force_arg_type(line[8], line[7]) \
                if not is_required else None
            g.add_hv_arg(
                arg_index=int(line[5][2:]) - 1,  # strip off the leading "\$" and make index zero-based
                name=line[6],
                value_type=line[7],
                default_value=default_value,
                required=is_required)

        try:  # this try will capture any critical errors
            for li in file_iterator:
                # remove width parameter
                line = self.__RE_WIDTH.sub("", li).split()

                if line[0] == "#N":
                    if line[1] == "canvas":
                        x = self.graph_from_canvas(
                            file_iterator,
                            file_hv_arg_dict,
                            canvas_line=li,
                            graph_args=graph_args,  # subpatch inherits parent graph arguments, including $0
                            pd_path=pd_path,
                            pos_x=int(line[2]),
                            pos_y=int(line[3]))
                        g.add_object(x)

                elif line[0] == "#X":
                    if line[1] == "restore":
                        if len(line) > 5 and line[5] == "@hv_obj":
                            obj_args = self.__resolve_object_args(
                                obj_type=line[6],
                                obj_args=line[7:],
                                graph=g,
                                raise_on_failure=False,
                                is_root=is_root)
                            if line[6] == "__switchcase":
                                x = HvSwitchcase(
                                    obj_type=line[6],
                                    obj_args=obj_args,
                                    pos_x=int(line[2]),
                                    pos_y=int(line[3]))
                            else:
                                x = HeavyObject(
                                    obj_type=line[6],
                                    obj_args=obj_args,
                                    pos_x=int(line[2]),
                                    pos_y=int(line[3]))
                            return x  # return a Heavy object instead of a graph
                        else:
                            # are we restoring an array object?
                            # do some final sanity checks
                            if obj_array is not None:
                                declared_size = obj_array.obj_dict["size"]
                                values_size = len(obj_array.obj_dict["values"])
                                if declared_size != values_size:
                                    new_size = max(declared_size, values_size)
                                    obj_array.add_warning(
                                        "Table \"{0}\" was declared as having {1} values, "
                                        "but {2} were supplied. It will be resized to {3} "
                                        "values (any unsupplied values will be zeroed).".format(
                                            obj_array.obj_dict["name"],
                                            declared_size,
                                            values_size,
                                            new_size))
                                    obj_array.obj_dict["size"] = new_size
                                    if new_size < declared_size:
                                        obj_array.obj_dict["values"] = obj_args["values"][:new_size]
                                    else:
                                        obj_array.obj_dict["values"].extend([0.0 for _ in
                                                                             range(new_size - declared_size)])
                                obj_array = None  # done parsing the array

                            # set the subpatch name
                            g.subpatch_name = " ".join(line[5:]) if len(line) > 5 else "subpatch"
                            return g  # pop the graph

                    elif line[1] == "text":
                        # @hv_arg arguments are pre-parsed
                        # TODO(mhroth): is it necessary to split the entire line at once?
                        # always add the comment to the graph, regardless
                        self.obj_counter["text"] += 1
                        g.add_object(HeavyObject(
                            obj_type="comment",
                            obj_args=[" ".join(line[4:])],
                            pos_x=int(line[2]),
                            pos_y=int(line[3])))

                    elif line[1] == "obj":
                        x = None  # a PdObject
                        if len(line) > 4:
                            obj_type = line[4]
                            # sometimes objects have $ arguments in them as well
                            obj_type = self.__resolve_object_args(
                                obj_type=obj_type,
                                obj_args=[obj_type],
                                graph=g,
                                is_root=is_root)[0]
                            obj_args = self.__resolve_object_args(
                                obj_type=obj_type,
                                obj_args=line[5:],
                                graph=g,
                                is_root=is_root)
                        else:
                            g.add_warning(
                                "This graph contains an empty object. "
                                "It should be removed or defined.",
                                NotificationEnum.WARNING_EMPTY_OBJECT)
                            g.add_object(HeavyObject(
                                obj_type="comment",
                                obj_args=["null object placeholder"],
                                pos_x=int(line[2]),
                                pos_y=int(line[3])))
                            continue

                        # do we have an abstraction for this object?
                        abs_path = self.find_abstraction_path(os.path.dirname(pd_path), obj_type)
                        if abs_path is not None and not g.is_abstraction_on_call_stack(abs_path):
                            # ensure that infinite recursion into abstractions is not possible
                            x = self.graph_from_file(
                                file_path=abs_path,
                                obj_args=obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]),
                                is_root=False)

                        # is this object in lib/pd_converted?
                        elif os.path.isfile(os.path.join(self.__PDLIB_CONVERTED_DIR, f"{obj_type}.hv.json")):
                            self.obj_counter[obj_type] += 1
                            hv_path = os.path.join(self.__PDLIB_CONVERTED_DIR, f"{obj_type}.hv.json")
                            x = HeavyGraph(
                                hv_path=hv_path,
                                obj_args=obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]))

                        # is this object in lib/heavy_converted?
                        elif os.path.isfile(os.path.join(self.__HVLIB_CONVERTED_DIR, f"{obj_type}.hv.json")):
                            self.obj_counter[obj_type] += 1
                            hv_path = os.path.join(self.__HVLIB_CONVERTED_DIR, f"{obj_type}.hv.json")
                            x = HeavyGraph(
                                hv_path=hv_path,
                                obj_args=obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]))

                        # is this object in lib/pd?
                        elif os.path.isfile(os.path.join(self.__PDLIB_DIR, f"{obj_type}.pd")):
                            self.obj_counter[obj_type] += 1
                            pdlib_path = os.path.join(self.__PDLIB_DIR, f"{obj_type}.pd")

                            # mapping of pd/lib abstraction objects to classes
                            # for checking connection validity
                            pd_class = {
                                "abs~": PdLibSignalGraph,
                                "clip~": PdLibSignalGraph,
                                "cos~": PdLibSignalGraph,
                                "dbtopow~": PdLibSignalGraph,
                                "dbtorms~": PdLibSignalGraph,
                                "exp~": PdLibSignalGraph,
                                "ftom~": PdLibSignalGraph,
                                "hip~": PdLibSignalGraph,
                                "lop~": PdLibSignalGraph,
                                "mtof~": PdLibSignalGraph,
                                "powtodb~": PdLibSignalGraph,
                                "q8_rsqrt~": PdLibSignalGraph,
                                "q8_sqrt~": PdLibSignalGraph,
                                "rmstodb~": PdLibSignalGraph,
                                "rsqrt~": PdLibSignalGraph,
                                "sqrt~": PdLibSignalGraph,
                                "wrap~": PdLibSignalGraph
                            }.get(obj_type, PdGraph)

                            x = self.graph_from_file(
                                file_path=pdlib_path,
                                obj_args=obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]),
                                is_root=False,
                                pd_graph_class=pd_class)

                            # register any object-specific warnings or errors
                            if obj_type in {"rzero~", "rzero_rev~", "czero~", "czero_rev~"}:
                                g.add_warning(
                                    f"[{obj_type}] accepts only signal input. "
                                    "Arguments and control connections are ignored.")

                        # is this object in lib/heavy?
                        elif os.path.isfile(os.path.join(self.__HVLIB_DIR, f"{obj_type}.pd")):
                            self.obj_counter[obj_type] += 1
                            hvlib_path = os.path.join(self.__HVLIB_DIR, f"{obj_type}.pd")
                            x = self.graph_from_file(
                                file_path=hvlib_path,
                                obj_args=obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]),
                                is_root=False)

                        # is this an object that must be programatically parsed?
                        elif obj_type in self.__PD_CLASSES:
                            self.obj_counter[obj_type] += 1
                            obj_class = self.__PD_CLASSES[obj_type]
                            x = obj_class(
                                obj_type,
                                obj_args,
                                pos_x=int(line[2]), pos_y=int(line[3]))

                        elif self.__is_float(obj_type):
                            # parse float literals
                            self.obj_counter["float"] += 1
                            x = HeavyObject(
                                obj_type="__var",
                                obj_args=[float(obj_type)],
                                pos_x=int(line[2]), pos_y=int(line[3]))

                        else:
                            g.add_error(
                                f"Don't know how to parse object \"{obj_type}\". Is it an "
                                "object supported by Heavy? Is it an abstraction? "
                                "Have the search paths been correctly configured?",
                                NotificationEnum.ERROR_UNKNOWN_OBJECT)
                            x = HeavyObject(
                                obj_type="comment",
                                obj_args=[f"null object placeholder ({obj_type})"])

                        g.add_object(x)

                    elif line[1] in {"floatatom", "symbolatom"}:
                        self.obj_counter[line[1]] += 1
                        x = self.graph_from_file(
                            file_path=os.path.join(self.__PDLIB_DIR, f"{line[1]}.pd"),
                            obj_args=[],
                            pos_x=int(line[2]), pos_y=int(line[3]),
                            is_root=False)
                        g.add_object(x)

                    elif line[1] == "array":
                        assert obj_array is None, "#X array object is already being parsed."
                        # array names can have dollar arguments in them.
                        # ensure that they are resolved
                        table_name = self.__resolve_object_args(
                            obj_type="array",
                            obj_args=[line[2]],
                            graph=g)[0]
                        # Pd encodes arrays with length greater than 999,999 with
                        # scientific notatation (e.g. 1e6) which Python's int() can't parse
                        table_size = int(decimal.Decimal(line[3]))
                        obj_array = HeavyObject(
                            obj_type="table",
                            # ensure that obj_array has its own values instance
                            obj_args=[table_name, table_size, []])
                        # TODO(mhroth): position information
                        g.add_object(obj_array)

                    elif line[1] == "msg":
                        self.obj_counter["msg"] += 1
                        g.add_object(PdMessageObject(
                            obj_type="msg",
                            obj_args=[" ".join(line[4:])],
                            pos_x=int(line[2]),
                            pos_y=int(line[3])))

                    elif line[1] == "connect":
                        g.add_parsed_connection(
                            from_index=int(line[2]),
                            from_outlet=int(line[3]),
                            to_index=int(line[4]),
                            to_inlet=int(line[5]))

                    elif line[1] == "declare":
                        if not is_root:
                            g.add_warning(
                                "[declare] objects are not supported in abstractions. "
                                "They can only be in the root canvas.")
                        elif len(line) >= 4 and line[2] == "-path":
                            did_add = self.add_relative_search_directory(line[3])
                            if not did_add:
                                g.add_warning(
                                    f"\"{line[3]}\" is not a valid relative abstraction "
                                    "search path. It will be ignored.")

                        else:
                            g.add_warning(
                                "Heavy only supports the -path flag for the "
                                "declare object.",
                                NotificationEnum.WARNING_DECLARE_PATH)

                    elif line[1] == "coords":
                        pass  # don't do anything with this command
                    elif line[1] == "f":
                        # A line such as "#X f 123"
                        # is found after a "#X restore" when the [pd afasdfasd]
                        # object's box has been resized
                        pass  # don't do anything with this command

                    else:
                        g.add_error(f"Don't know how to parse line: {' '.join(line)}")

                elif line[0] == "#A" and obj_array is not None:
                    obj_array.obj_dict["values"].extend([float(f) for f in line[2:]])

                else:
                    g.add_error(f"Don't know how to parse line: {' '.join(line)}")

        except Exception as e:
            # bubble the Exception back to the root graph where the graph
            # will be returned
            if not g.is_root:
                raise e
            else:
                # NOTE(mhroth): should the exception be added as an error?
                # Sometimes it's all that we have, so perhaps it's a good idea.
                g.add_error(str(e), NotificationEnum.ERROR_EXCEPTION)

        return g

    @classmethod
    def __resolve_object_args(
        cls,
        obj_type: str,
        obj_args: List,
        graph: PdGraph,
        raise_on_failure: bool = True,
        is_root: bool = False
    ) -> Any:
        """ Resolve object arguments against the given graph arguments.
            By default this function raises an Exception if it cannot resolve an
            argument.
            This behaviour may be disabled, in which case the unresolved argument
            is replaced with None (which is an otherwise invalid value). A value of
            None typically indicates to a HeavyObject that the default value
            may be used.
        """
        # TODO(mhroth): can this be done more elegantly?
        resolved_obj_args = list(obj_args)  # make a copy of the original obj_args
        for i, a in enumerate(obj_args):
            for m in set(cls.__RE_DOLLAR.findall(a)):
                x = int(m)  # the dollar index (i.e. $x)
                if len(graph.obj_args) > x:
                    a = a.replace(fr"\${m}", str(graph.obj_args[x]))

                # check if hv_args can be used to supply a default value
                elif len(graph.hv_args) > (x - 1):  # heavy args are zero-indexed
                    if not graph.hv_args[x - 1]["required"]:
                        a = a.replace(fr"\${m}", str(graph.hv_args[x - 1]["default"]))
                    else:
                        graph.add_error(
                            f"There is a missing required argument named \"{graph.hv_args[x - 1]['name']}\".",
                            NotificationEnum.ERROR_MISSING_REQUIRED_ARGUMENT)

                elif is_root:
                    # NOTE(mhroth): this case is questionable, but since Pd
                    # defaults to this behavior without warning, so will we.
                    # graph.add_warning(
                    #     "${0} in \"{1}\" in the top-level graph is resolved to "
                    #     "\"0\". It is recommended that you remove $-arguments "
                    #     "from the top-level graph.".format(m, a))
                    a = a.replace(fr"\${m}", "0")

                else:
                    if raise_on_failure:
                        # NOTE(mhroth): this case is questionable, but since Pd
                        # defaults to this behavior without warning, so will we.
                        # graph.add_warning(
                        #     "Object [{0}] requires argument \"{1}\" but the parent "
                        #     "patch does not provide one ({2}). A default value of "
                        #     "\"0\" will be used.".format(obj_type, a, graph.obj_args))
                        a = a.replace(fr"\${m}", "0")
                    else:
                        a = None  # indicate that this argument could not be resolved by replacing it with None
            resolved_obj_args[i] = a
        return resolved_obj_args

    # a mapping of Pd objects to the classes that will parse them
    __PD_CLASSES = {
        "adc~": PdAudioIoObject,
        "dac~": PdAudioIoObject,
        "inlet": PdLetObject,
        "inlet~": PdLetObject,
        "outlet": PdLetObject,
        "outlet~": PdLetObject,
        "pack": PdPackObject,
        "pd": PdGraph,
        "route": PdRouteObject,
        "sel": PdSelectObject,
        "select": PdSelectObject,
        "t": PdTriggerObject,
        "trigger": PdTriggerObject,
        "table": PdTableObject,
        "unpack": PdUnpackObject,
        "s": PdSendObject,
        "send": PdSendObject,
        "s~": PdSendObject,
        "send~": PdSendObject,
        "throw~": PdSendObject,
        "r": PdReceiveObject,
        "receive": PdReceiveObject,
        "r~": PdReceiveObject,
        "receive~": PdReceiveObject,
        "catch~": PdReceiveObject
    }

    # fill in as much of __PD_CLASSES programmatically as possible
    for o in PdBinopObject.get_supported_objects():
        __PD_CLASSES[o] = PdBinopObject

    @classmethod
    def __is_float(cls, x: int) -> bool:
        """ Returns True if the input can be converted to a float. False otherwise.
        """
        try:
            float(x)
            return True
        except Exception:
            return False
