# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

import json
import os

from .HeavyObject import HeavyObject
from .MaxAdcObject import MaxAdcObject
from .MaxBinopObject import MaxBinopObject
from .MaxDacObject import MaxDacObject
from .MaxGraph import MaxGraph
from .MaxInletObject import MaxInletObject
from .MaxOutletObject import MaxOutletObject
from .MaxUnopObject import MaxUnopObject


class MaxParser:

    @classmethod
    def graph_from_file(clazz, file_path, obj_id=None, obj_args=None):
        with open(file_path, "r") as f:
            graph_obj = json.loads(f.read())

        return MaxParser.graph_from_object(graph_obj, obj_id, obj_args, file_path)

    @classmethod
    def graph_from_object(clazz, obj, obj_id=None, obj_args=None, max_path=None):
        g = MaxGraph(obj_args=obj_args, obj_id=obj_id, max_path=max_path)

        # parse objects
        for o in obj["patcher"]["boxes"]:
            o = o["box"]  # the max object dictionary
            x = None  # a MaxObject

            # read common parameters
            obj_id = o["id"]
            patching_rect = o["patching_rect"]

            if o["maxclass"] == "newobj":
                obj_text = o["text"].split()
                obj_type = obj_text[0]
                obj_args = obj_text[1:] if len(obj_text) > 1 else []

                # resolve object arguments against graph arguments
                for i, a in enumerate(obj_args):
                    if a.startswith("$"):
                        x = int(a[1:]) - 1
                        if len(g.obj_args) > x:
                            obj_args[i] = g.obj_args[x]
                        else:
                            print("WARNING: Can't resolve object argument {0} against graph arguments: {1}".format(
                                a,
                                g.obj_args))

                # are we dealing with a declared Heavy object?
                if obj_type == "patcher":
                    if len(obj_args) > 0 and obj_args[0] == "@hv_obj":
                        if len(obj_args) > 1 and HeavyObject.is_heavy(obj_args[1]):
                            # initialise heavy object
                            x = HeavyObject(
                                obj_args[1], obj_args[2:], obj_id,
                                pos_x=patching_rect[0], pos_y=patching_rect[1])
                        else:
                            raise Exception("Max subpatch has @hv_obj annotation but declares no Heavy object.")
                    else:
                        # TODO(mhroth): assume that this is a normal max subpatch
                        raise Exception("Cannot parse Max subpatches yet.")

                # do we have an abstraction for this max object? Is it in the maxlib?
                # TODO(mhroth): are there any other search paths to look through?
                elif os.path.isfile(os.path.join(os.path.dirname(__file__), "maxlib", obj_type + ".maxpat")):
                    max_path = os.path.join(os.path.dirname(__file__), "maxlib", obj_type + ".maxpat")
                    x = MaxParser.graph_from_file(max_path, obj_id, obj_args)

                # is this an object that must be programmatically parsed?
                elif obj_type in MaxParser.__MAX_CLASSES:
                    clazz = MaxParser.__MAX_CLASSES[obj_type]
                    x = clazz(
                        obj_type, obj_args, obj_id,
                        pos_x=patching_rect[0], pos_y=patching_rect[1])

                else:
                    raise Exception("Don't know how to parse object \"{0}\".".format(obj_type))

            elif o["maxclass"] == "inlet":
                outlet_type = o["outlettype"][0]
                x = MaxInletObject(
                    outlet_type, obj_id,
                    pos_x=patching_rect[0], pos_y=patching_rect[1])

            elif o["maxclass"] == "outlet":
                # TODO(mhroth): correctly determine connection type of outlet
                x = MaxOutletObject(
                    "signal", obj_id,
                    pos_x=patching_rect[0], pos_y=patching_rect[1])

            else:
                print("WARNING: Ignoring maxclass \"{0}\".".format(o["maxclass"]))
                continue  # ignore comments, etc.

            g.add_object(x)

        # parse connections
        for li in obj["patcher"]["lines"]:
            li = li["patchline"]
            if not (bool(li["disabled"]) or bool(li["hidden"])):
                g.add_connection(
                    from_id=li["source"][0],
                    from_outlet=li["source"][1],
                    to_id=li["destination"][0],
                    to_inlet=li["destination"][1])

        return g

    # a mapping of Max objects to the classes that will parse them
    __MAX_CLASSES = {
        "adc~": MaxAdcObject,
        "dac~": MaxDacObject
    }
    # fill in as much of __MAX_CLASSES programmatically as possible
    for o in MaxUnopObject.get_supported_objects():
        __MAX_CLASSES[o] = MaxUnopObject
    for o in MaxBinopObject.get_supported_objects():
        __MAX_CLASSES[o] = MaxBinopObject
