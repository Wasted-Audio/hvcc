import json
from pathlib import Path

import jinja2

from hvcc.types.GUI import Canvas, Comment, Graph, GraphRoot, GUIObjects
from hvcc.types.meta import DPF


def open_gui_json(
    patch_name: str,
    c_src_dir: Path,
) -> GraphRoot:

    # load GUI from json file
    gui_json_path = Path(c_src_dir, "../ir/", f"{patch_name}.heavy.gui.json")
    with open(gui_json_path, "r") as f:
        gui_json = GraphRoot(**json.load(f))

    return gui_json


def nanovg_render(
    patch_name: str,
    c_src_dir: Path,
    env: jinja2.Environment,
    recv_list: list,
    send_list: list,
    meta: DPF
) -> tuple[
    GraphRoot,
    dict[str, list[str]],
    list[str]
]:
    """ Generate nanovg components from the GUI json
    """
    gui_json = open_gui_json(patch_name, c_src_dir)

    # widget overview
    widgets: dict[str, list[str]] = {
        "graph": [],
        "canvas": [],
        "comment": [],
        "bang": [],
        "toggle": [],
        "vradio": [],
        "hradio": [],
        "vslider": [],
        "hslider": [],
        "knob": [],
        "number": [],
        "float": []
    }

    # render gui objects
    gui_objects_render = []

    def generate_gui_objects(objects: list[GUIObjects], parent: str):
        for w in objects:
            if isinstance(w, Graph):
                widgets["graph"].append(w.id)
                gui_objects_render.append(
                    f"""
    // subpatch
    {w.id} = new PDSubpatch({parent});
    {w.id}->setSize({w.size.x} * scaleFactor, {w.size.y} * scaleFactor);
    {w.id}->setAbsolutePos({w.position.x} * scaleFactor, {w.position.y} * scaleFactor);
    {parent}->addManagedChild({w.id});
                    """
                )
                generate_gui_objects(w.objects, w.id)
            else:
                if w.type == "popmenu":
                    continue
                widgets[w.type].append(w.id if isinstance(w, (Canvas, Comment)) else w.parameter)

                gui_objects_render.append(env.get_template("gui_objects.cpp").render(
                    parent=parent,
                    gui_objects=[w],
                    receivers=recv_list,
                    senders=send_list,
                    meta=meta
                ))

    generate_gui_objects(gui_json.objects, "mainPatch")


    return gui_json, widgets, gui_objects_render
