from pytest import fixture


from hvcc.types.GUI import Coords, Size, Color, Canvas, VRadio, HRadio


@fixture
def cnv_vis1():
    return Canvas(
        position=Coords(x=0, y=0),
        size=Size(x=100, y=100),
        bg_color=Color("blue")
    )


@fixture
def cnv_vis2():
    return Canvas(
        position=Coords(x=-50, y=-50),
        size=Size(x=100, y=100),
        bg_color=Color("blue")
    )


@fixture
def cnv_invis1():
    return Canvas(
        position=Coords(x=100, y=100),
        size=Size(x=100, y=100),
        bg_color=Color("red")
    )


@fixture
def cnv_invis2():
    return Canvas(
        position=Coords(x=-100, y=-100),
        size=Size(x=100, y=100),
        bg_color=Color("red")
    )


@fixture
def radio_vis1():
    options = 3
    return VRadio(
        position=Coords(x=0, y=0),
        size=Size(x=10, y=(options * 10)),
        parameter="something1",
        bg_color=Color("red"),
        fg_color=Color("blue"),
        options=options
    )


@fixture
def radio_vis2():
    options = 4
    return HRadio(
        position=Coords(x=-10, y=-5),
        size=Size(x=(options * 10), y=10),
        parameter="something2",
        bg_color=Color("red"),
        fg_color=Color("blue"),
        options=options
    )


@fixture
def radio_invis1():
    options = 3
    return VRadio(
        position=Coords(x=-110, y=-100 - (options * 10)),
        size=Size(x=10, y=(options * 10)),
        parameter="something1",
        bg_color=Color("red"),
        fg_color=Color("blue"),
        options=options
    )


@fixture
def radio_invis2():
    options = 4
    return HRadio(
        position=Coords(x=100, y=100),
        size=Size(x=(options * 10), y=10),
        parameter="something2",
        bg_color=Color("red"),
        fg_color=Color("blue"),
        options=options
    )
