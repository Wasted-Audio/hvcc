import json
import os

import jinja2

from hvcc.types.GUI import Canvas, Comment, GraphBase, Graph, GUIObjects


def nanovg_render(
    patch_name: str,
    c_src_dir: str,
    env: jinja2.Environment,
    recv_list: list,
    send_list: list
) -> tuple[
    GraphBase,
    dict[str, list[str]],
    list[str]
]:
    """ Generate nanovg components from the GUI json
    """

    # load GUI json
    gui_json_path = os.path.join(c_src_dir, "../ir/", f"{patch_name}.heavy.gui.json")
    with open(gui_json_path, "r") as f:
        gui_json = GraphBase(**json.load(f))

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

    def generate_gui_objects(graphs: list[Graph], objects: list[GUIObjects], parent: str):
        for w in objects:
            widgets[w.type].append(w.id if isinstance(w, (Canvas, Comment)) else w.parameter)

        gui_objects_render.append(env.get_template("gui_objects.cpp").render(
            parent=parent,
            gui_objects=objects,
            receivers=recv_list,
            senders=send_list
        ))

        for graph in graphs:
            widgets["graph"].append(graph.id)

            gui_objects_render.append(
                f"""
    // subpatch
    {graph.id} = new PDSubpatch({parent});
    {graph.id}->setSize({graph.gop_size.x} * scaleFactor, {graph.gop_size.y} * scaleFactor);
    {graph.id}->setAbsolutePos({graph.position.x} * scaleFactor, {graph.position.y} * scaleFactor);
    {parent}->addManagedChild({graph.id});
                """
                    )
            generate_gui_objects(graph.graphs, graph.objects, graph.id)

    generate_gui_objects(gui_json.graphs, gui_json.objects, "mainPatch")

    return gui_json, widgets, gui_objects_render
