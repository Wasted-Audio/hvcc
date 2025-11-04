from hvcc.interpreters.pd2gui.PdGUIParser import PdGUIParser
from hvcc.types.GUI import Graph, Canvas, Coords, Color, Size


def test_graph_filter():
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
        objects=[]
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
        objects=[]
    )

    g_invis2 = Graph(
        position=Coords(x=-100, y=-100),
        gop_start=Coords(),
        gop_size=Size(x=100, y=100),
        graphs=[],
        objects=[]
    )

    graph_list = [g_vis, g_vis2, g_invis, g_invis2]
    filtered_graphs = p.filter_invisible_graphs(graph_list, g.gop_start, g.gop_size)

    assert filtered_graphs == [g_vis, g_vis2]
