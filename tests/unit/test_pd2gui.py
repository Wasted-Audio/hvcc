from hvcc.interpreters.pd2gui.PdGUIParser import PdGUIParser
from hvcc.types.GUI import Graph, Coords, Size, GUIObjects


def test_filter_graph(cnv_vis1):
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    g_vis = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[cnv_vis1]
    )

    g_vis2 = Graph(
        position=Coords(x=-50, y=-50),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    g_invis = Graph(
        position=Coords(x=100, y=100),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[cnv_vis1]
    )

    g_invis2 = Graph(
        position=Coords(x=-100, y=-100),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[cnv_vis1]
    )

    graph_list = [g_vis, g_vis2, g_invis, g_invis2]
    filtered_graphs = p.filter_invisible_graphs(graph_list, g.gop_start, g.gop_size)

    assert filtered_graphs == [g_vis]


def test_filter_nested_graph(cnv_vis1):
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    g_nested_child = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[cnv_vis1]
    )

    g_nested_parent = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[g_nested_child],
        objects=[]
    )

    g_nested_empty = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    filtered_graphs = p.filter_invisible_graphs([g_nested_parent, g_nested_empty], g.gop_start, g.gop_size)

    assert filtered_graphs == [g_nested_parent]


def test_filter_object_canvas(
    cnv_vis1,
    cnv_vis2,
    cnv_invis1,
    cnv_invis2
):
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    objects: list[GUIObjects] = [cnv_vis1, cnv_vis2, cnv_invis1, cnv_invis2]
    filtered_objects = p.filter_invisible_objects(objects, g.gop_start, g.gop_size)

    assert filtered_objects == [cnv_vis1, cnv_vis2]


def test_filter_object_radio(
    radio_vis1,
    radio_vis2,
    radio_invis1,
    radio_invis2
):
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    objects: list[GUIObjects] = [radio_vis1, radio_vis2, radio_invis1, radio_invis2]
    filtered_objects = p.filter_invisible_objects(objects, g.gop_start, g.gop_size)

    assert filtered_objects == [radio_vis1, radio_vis2]


def test_filter_params():
    p = PdGUIParser()

    param1 = "vol @hv_param"
    param2 = "volume"

    assert p.filter_params(param1) == "vol"
    assert p.filter_params(param2) is None
