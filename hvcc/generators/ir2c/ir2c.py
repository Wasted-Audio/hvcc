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

import argparse
import jinja2
import json
import os
import shutil
import time

from collections import Counter
from collections import OrderedDict
from typing import Dict, List, Optional, Type, Union

from hvcc.generators.ir2c.PrettyfyC import PrettyfyC
from hvcc.generators.copyright import copyright_manager

from hvcc.generators.ir2c.ControlBinop import ControlBinop
from hvcc.generators.ir2c.ControlCast import ControlCast
from hvcc.generators.ir2c.ControlDelay import ControlDelay
from hvcc.generators.ir2c.ControlIf import ControlIf
from hvcc.generators.ir2c.ControlMessage import ControlMessage
from hvcc.generators.ir2c.ControlPack import ControlPack
from hvcc.generators.ir2c.ControlPrint import ControlPrint
from hvcc.generators.ir2c.ControlReceive import ControlReceive
from hvcc.generators.ir2c.ControlRandom import ControlRandom
from hvcc.generators.ir2c.ControlSend import ControlSend
from hvcc.generators.ir2c.ControlSlice import ControlSlice
from hvcc.generators.ir2c.ControlSwitchcase import ControlSwitchcase
from hvcc.generators.ir2c.ControlSystem import ControlSystem
from hvcc.generators.ir2c.ControlTabhead import ControlTabhead
from hvcc.generators.ir2c.ControlTabread import ControlTabread
from hvcc.generators.ir2c.ControlTabwrite import ControlTabwrite
from hvcc.generators.ir2c.ControlUnop import ControlUnop
from hvcc.generators.ir2c.ControlVar import ControlVar
from hvcc.generators.ir2c.HeavyObject import HeavyObject
from hvcc.generators.ir2c.HeavyTable import HeavyTable
from hvcc.generators.ir2c.SignalConvolution import SignalConvolution
from hvcc.generators.ir2c.SignalBiquad import SignalBiquad
from hvcc.generators.ir2c.SignalCPole import SignalCPole
from hvcc.generators.ir2c.SignalDel1 import SignalDel1
from hvcc.generators.ir2c.SignalEnvelope import SignalEnvelope
from hvcc.generators.ir2c.SignalLine import SignalLine
from hvcc.generators.ir2c.SignalLorenz import SignalLorenz
from hvcc.generators.ir2c.SignalMath import SignalMath
from hvcc.generators.ir2c.SignalPhasor import SignalPhasor
from hvcc.generators.ir2c.SignalRPole import SignalRPole
from hvcc.generators.ir2c.SignalSample import SignalSample
from hvcc.generators.ir2c.SignalSamphold import SignalSamphold
from hvcc.generators.ir2c.SignalTabhead import SignalTabhead
from hvcc.generators.ir2c.SignalTabread import SignalTabread
from hvcc.generators.ir2c.SignalTabwrite import SignalTabwrite
from hvcc.generators.ir2c.SignalVar import SignalVar


class ir2c:

    __OBJECT_CLASS_DICT = {
        "__delay": ControlDelay,
        "__if": ControlIf,
        "__print": ControlPrint,
        "__random": ControlRandom,
        "__var": ControlVar,
        "__table": HeavyTable,
        "__cast_b": ControlCast,
        "__cast_f": ControlCast,
        "__cast_s": ControlCast,
        "__message": ControlMessage,
        "__system": ControlSystem,
        "__receive": ControlReceive,
        "__switchcase": ControlSwitchcase,
        "__conv~f": SignalConvolution,
        "__biquad~f": SignalBiquad,
        "__biquad_k~f": SignalBiquad,
        "__env~f": SignalEnvelope,
        "__line~f": SignalLine,
        "__lorenz~f": SignalLorenz,
        "__del1~f": SignalDel1,
        "__tabread~if": SignalTabread,
        "__tabread~f": SignalTabread,
        "__tabreadu~f": SignalTabread,
        "__tabread_stoppable~f": SignalTabread,
        "__tabhead~f": SignalTabhead,
        "__tabwrite~f": SignalTabwrite,
        "__tabwrite_stoppable~f": SignalTabwrite,
        "__phasor~f": SignalPhasor,
        "__phasor_k~f": SignalPhasor,
        "__sample~f": SignalSample,
        "__samphold~f": SignalSamphold,
        "__slice": ControlSlice,
        "__send": ControlSend,
        "__tabhead": ControlTabhead,
        "__tabread": ControlTabread,
        "__tabwrite": ControlTabwrite,
        "__pack": ControlPack,
        "__rpole~f": SignalRPole,
        "__cpole~f": SignalCPole
    }

    # the base set of C files necessary for the patch
    __BASE_FILE_SET = {
        "HeavyContextInterface.hpp",
        "HeavyContext.hpp", "HeavyContext.cpp",
        "HvHeavy.h", "HvHeavyInternal.h", "HvHeavy.cpp",
        "HvUtils.h", "HvUtils.c", "HvMath.h",
        "HvMessageQueue.h", "HvMessageQueue.c",
        "HvMessagePool.h", "HvMessagePool.c",
        "HvTable.h", "HvTable.c",
        "HvMessage.h", "HvMessage.c",
        "HvLightPipe.h", "HvLightPipe.c"
    }

    @classmethod
    def filter_hvhash(cls, x: Union[float, str]) -> str:
        """ Return the hash string of an object.
        """
        return HeavyObject.get_hash_string(x)

    @classmethod
    def filter_extern(cls, d: Dict) -> Dict:
        """ Return a dictionary of objects that are externed.
        """
        return {k: v for k, v in d.items() if v["extern"]}

    @classmethod
    def get_class(cls, obj_type: str) -> Type[HeavyObject]:
        if SignalMath.handles_type(obj_type):
            return SignalMath
        elif ControlBinop.handles_type(obj_type):
            return ControlBinop
        elif ControlUnop.handles_type(obj_type):
            return ControlUnop
        elif SignalVar.handles_type(obj_type):
            return SignalVar
        elif obj_type in ir2c.__OBJECT_CLASS_DICT:
            return ir2c.__OBJECT_CLASS_DICT[obj_type]
        else:
            raise Exception(f"No class found for object type \"{obj_type}\".")

    @classmethod
    def compile(
        cls,
        hv_ir_path: str,
        static_dir: str,
        output_dir: str,
        externs: Dict,
        copyright: Optional[str] = None
    ) -> Dict:
        """ Compiles a HeavyIR file into a C.
            Returns a tuple of compile time in seconds, a notification dictionary,
            and a HeavyIR object counter.
        """

        # keep track of the total compile time
        tick = time.time()

        # establish the jinja environment
        env = jinja2.Environment()
        env.filters["hvhash"] = cls.filter_hvhash
        env.filters["extern"] = cls.filter_extern
        env.loader = jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates"))

        # read the hv.ir.json file
        with open(hv_ir_path, "r") as f:
            ir = json.load(f)

        # generate the copyright
        copyright = copyright_manager.get_copyright_for_c(copyright)

        #
        # Parse the hv.ir data structure and generate C-language strings.
        #

        # generate set of header files to include
        include_set = set([x for o in ir["objects"].values() for x in ir2c.get_class(o["type"]).get_C_header_set()])

        # generate set of files to add to project
        file_set = set([x for o in ir["objects"].values() for x in ir2c.get_class(o["type"]).get_C_file_set()])
        file_set.update(ir2c.__BASE_FILE_SET)

        # generate object definition and initialisation list
        init_list: List = []
        free_list = []
        def_list = []
        decl_list = []
        for obj_id in ir["init"]["order"]:
            o = ir["objects"][obj_id]
            obj_class = ir2c.get_class(o["type"])
            init_list.extend(obj_class.get_C_init(o["type"], obj_id, o["args"]))
            def_list.extend(obj_class.get_C_def(o["type"], obj_id))
            free_list.extend(obj_class.get_C_free(o["type"], obj_id, o["args"]))

        impl_list = []
        for x in ir["control"]["sendMessage"]:
            obj_id = x["id"]
            o = ir["objects"][obj_id]
            obj_class = ir2c.get_class(o["type"])
            impl = obj_class.get_C_impl(
                o["type"],
                obj_id,
                x["onMessage"],
                ir2c.get_class,
                ir["objects"])
            impl_list.append("\n".join(PrettyfyC.prettyfy_list(impl)))
            decl_list.extend(obj_class.get_C_decl(o["type"], obj_id, o["args"]))

        # generate static table data initialisers
        table_data_list: List = []
        for k, v in ir["tables"].items():
            o = ir["objects"][v["id"]]
            obj_class = ir2c.get_class(o["type"])
            table_data_list.extend(obj_class.get_table_data_decl(
                o["type"],
                v["id"],
                o["args"]))

        # generate the list of functions to process
        process_list: List = []
        for x in ir["signal"]["processOrder"]:
            obj_id = x["id"]
            o = ir["objects"][obj_id]
            process_list.extend(ir2c.get_class(o["type"]).get_C_process(
                x,
                o["type"],
                obj_id,
                o["args"]))

        #
        # Load the C-language template files and use the parsed strings to fill them in.
        #

        # make the output directory if necessary
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # the project name to be used as a part of file and function names
        name = ir["name"]["escaped"]

        # ensure that send_receive dictionary is alphabetised by the receiver key
        send_receive = OrderedDict(sorted([(k, v) for k, v in ir["control"]["receivers"].items()], key=lambda x: x[0]))

        # write HeavyContext.h
        with open(os.path.join(output_dir, f"Heavy_{name}.hpp"), "w") as f:
            f.write(env.get_template("Heavy_NAME.hpp").render(
                name=name,
                include_set=include_set,
                decl_list=decl_list,
                def_list=def_list,
                signal=ir["signal"],
                copyright=copyright,
                externs=externs))

        # write C++ implementation
        with open(os.path.join(output_dir, f"Heavy_{name}.cpp"), "w") as f:
            f.write(env.get_template("Heavy_NAME.cpp").render(
                name=name,
                signal=ir["signal"],
                init_list=init_list,
                free_list=free_list,
                impl_list=impl_list,
                send_receive=send_receive,
                send_table=ir["tables"],
                process_list=process_list,
                table_data_list=table_data_list,
                copyright=copyright))

        # write C API, hv_NAME.h
        with open(os.path.join(output_dir, f"Heavy_{name}.h"), "w") as f:
            f.write(env.get_template("Heavy_NAME.h").render(
                name=name,
                copyright=copyright,
                externs=externs))

        # copy static files to output directory
        for f in file_set:
            shutil.copy2(
                src=os.path.join(static_dir, str(f)),
                dst=os.path.join(output_dir, str(f)))

        # generate HeavyIR object counter
        ir_counter = Counter([obj["type"] for obj in ir["objects"].values()])

        return {
            "stage": "ir2c",
            "notifs": {
                "has_error": False,
                "exception": None,
                "errors": []
            },
            "in_dir": os.path.dirname(hv_ir_path),
            "in_file": os.path.basename(hv_ir_path),
            "out_dir": output_dir,
            "out_file": "",
            "compile_time": (time.time() - tick),
            "obj_counter": ir_counter
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="A Heavy.IR to C-language translator.")
    parser.add_argument(
        "hv_ir_path",
        help="The path to the Heavy.IR file to read.")
    parser.add_argument(
        "--static_dir",
        default="./static",
        help="The path to the static C files.")
    parser.add_argument(
        "--output_dir",
        default="./out",
        help="")
    parser.add_argument(
        "--copyright",
        default=None,
        help="A string indicating the owner of the copyright.")
    parser.add_argument("-v", "--verbose", action="count")
    args = parser.parse_args()

    externs = {
        "parameters": {
            "in": {},
            "out": {}
        },
        "events": {}
    }

    results = ir2c.compile(
        args.hv_ir_path,
        args.static_dir,
        args.output_dir,
        externs,
        args.copyright)

    if args.verbose:
        print("Total ir2c time: {0:.2f}ms".format(results["compile_time"] * 1000))


if __name__ == "__main__":
    main()
