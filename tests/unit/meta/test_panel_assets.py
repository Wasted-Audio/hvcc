
from pydantic_extra_types.color import Color

from hvcc.generators.c2meta.panel_gen import DEFAULT_PANEL_COLOR, PANEL_HEIGHT, PANEL_MIN_WIDTH, layout_panel_assets
from hvcc.generators.c2meta.panel_val import ensure_panel_assets
from hvcc.types.compiler import ExternInfo, ExternParams
from hvcc.types.meta import MetaModule, metaPlugin
from hvcc.types.metamodule import Assets, Panel


def test_panel_color_only():
    assets = Assets(
        panel=Panel(color=Color("#ff0000"))
    )

    new_assets = layout_panel_assets(assets)

    assert new_assets.panel is not None and assets.panel is not None
    assert new_assets.panel.color == assets.panel.color
    assert new_assets.panel.x == PANEL_MIN_WIDTH
    assert new_assets.panel.y == PANEL_HEIGHT


def test_panel_coordinates_only():
    assets = Assets(
        panel=Panel(x=40, y=PANEL_HEIGHT)
    )

    new_assets = layout_panel_assets(assets)

    assert new_assets.panel is not None and assets.panel is not None
    assert new_assets.panel.color == Color(DEFAULT_PANEL_COLOR)
    assert new_assets.panel.x == 40


def test_ensure_panel_assets_color_only_panel():
    """Colour-only panel with no components must get x/y set."""

    mm = MetaModule(modules=[metaPlugin(assets=Assets(panel=Panel(color=Color("#ff0000"))))])
    externs = ExternInfo(parameters=ExternParams(inParam=[], outParam=[]))
    assets = ensure_panel_assets(mm, externs, 0, 0)

    assert assets.panel is not None
    assert assets.panel.color == Color("#ff0000")
    assert assets.panel.x == PANEL_MIN_WIDTH
    assert assets.panel.y == PANEL_HEIGHT
