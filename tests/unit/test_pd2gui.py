from hvcc.interpreters.pd2gui.PdGUIParser import PdGUIParser
from hvcc.types.GUI import Graph, Canvas, Coords, Color, Size, GUIObjects


def test_filter_graph():
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    c = Canvas(
        position=Coords(x=0, y=0),
        size=Size(x=100, y=100),
        bg_color=Color("grey")
    )

    g.objects = [c]

    g_vis = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[c]
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
        objects=[c]
    )

    g_invis2 = Graph(
        position=Coords(x=-100, y=-100),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[c]
    )

    graph_list = [g_vis, g_vis2, g_invis, g_invis2]
    filtered_graphs = p.filter_invisible_graphs(graph_list, g.gop_start, g.gop_size)

    assert filtered_graphs == [g_vis]


def test_filter_object_canvas():
    p = PdGUIParser()
    g = Graph(
        position=Coords(x=0, y=0),
        gop_start=Coords(x=0, y=0),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    c_vis = Canvas(
        position=Coords(x=0, y=0),
        size=Size(x=100, y=100),
        bg_color=Color("blue")
    )

    c_vis2 = Canvas(
        position=Coords(x=-50, y=-50),
        size=Size(x=100, y=100),
        bg_color=Color("blue")
    )

    c_invis = Canvas(
        position=Coords(x=100, y=100),
        size=Size(x=100, y=100),
        bg_color=Color("red")
    )

    c_invis2 = Canvas(
        position=Coords(x=-100, y=-100),
        size=Size(x=100, y=100),
        bg_color=Color("red")
    )

    objects: list[GUIObjects] = [c_vis, c_vis2, c_invis, c_invis2]
    filtered_objects = p.filter_invisible_objects(objects, g.gop_start, g.gop_size)

    assert filtered_objects == [c_vis, c_vis2]
