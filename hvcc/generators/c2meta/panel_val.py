# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only


from hvcc.types.compiler import ExternInfo
from hvcc.types.meta import MetaModule
from hvcc.types.metamodule import Assets, Input, Knob, Led, Output, UIElement

from .panel_gen import image_size, layout_panel_assets


def _reconcile_components(
    user_assets: Assets | None,
    externs: ExternInfo,
    num_inputs: int,
    num_outputs: int
) -> tuple[list[Knob], list[Led], list[Input], list[Output]]:
    # Knobs: map by param display name
    user_knobs = {k.param: k for k in (user_assets.knobs if user_assets else [])}
    knobs = [
        user_knobs.get(p.display, Knob(param=p.display))
        for _, p in externs.parameters.inParam
    ]

    # LEDs: map by sender display name
    user_leds = {l.led: l for l in (user_assets.leds if user_assets else [])}
    leds = [
        user_leds.get(p.display, Led(led=p.display))
        for _, p in externs.parameters.outParam
        if p.display is not None
    ]

    # Inputs: map by port ID (1-indexed)
    user_inputs = {i.id: i for i in (user_assets.inputs if user_assets else [])}
    inputs = [
        user_inputs.get(ch, Input(id=ch))
        for ch in range(1, num_inputs + 1)
    ]

    # Outputs: map by port ID (1-indexed)
    user_outputs = {o.id: o for o in (user_assets.outputs if user_assets else [])}
    outputs = [
        user_outputs.get(ch, Output(id=ch))
        for ch in range(1, num_outputs + 1)
    ]

    return knobs, leds, inputs, outputs


def _is_configuration_complete(
    assets: Assets | None,
    externs: ExternInfo,
    num_inputs: int,
    num_outputs: int,
) -> bool:
    """Return True if panel and all components are fully specified with coordinates."""

    if assets is None or assets.panel is None or assets.panel.image is None:
        return False
    if assets.panel.x is None or assets.panel.y != 240:
        return False

    elements: list[UIElement] = [*assets.knobs, *assets.leds, *assets.inputs, *assets.outputs]
    if any(el.x is None or el.y is None for el in elements):
        return False

    # Verify complete coverage of externs and audio channels
    knob_params = {k.param for k in assets.knobs}
    if not all(p.display in knob_params for _, p in externs.parameters.inParam):
        return False

    led_names = {l.led for l in assets.leds}
    if not all(p.display in led_names for _, p in externs.parameters.outParam if p.display):
        return False

    input_ids = {i.id for i in assets.inputs}
    if input_ids != set(range(1, num_inputs + 1)):
        return False

    output_ids = {o.id for o in assets.outputs}
    return output_ids == set(range(1, num_outputs + 1))


def ensure_panel_assets(
    mm_meta: MetaModule,
    externs: ExternInfo,
    num_input_channels: int,
    num_output_channels: int,
    verbose: bool | None = False
) -> Assets:
    """Return the module's assets, generating a default panel if none exist."""
    if not mm_meta.modules:
        raise ValueError("--> c2meta: meta.modules must contain at least one module")

    module = mm_meta.modules[0]
    assets = module.assets or Assets()

    # Resolve panel image dimensions if provided
    if assets.panel and assets.panel.image and (assets.panel.x is None or assets.panel.y is None):
        w, h = image_size(assets.panel.image)
        if h != 240:
            raise ValueError(f"Panel height must be 240 pixels (got {h})")
        assets.panel.x, assets.panel.y = w, h

    # Early exit if configuration is 100% complete
    if _is_configuration_complete(assets, externs, num_input_channels, num_output_channels):
        return assets

    if verbose:
        print("--> c2meta: generating custom panel")

    # Reconcile user-provided elements with patch externs (preserve custom images)
    knobs, leds, inputs, outputs = _reconcile_components(
        assets, externs, num_input_channels, num_output_channels
    )
    assets.knobs = knobs
    assets.leds = leds
    assets.inputs = inputs
    assets.outputs = outputs

    # Auto-layout if any component is missing coordinates
    all_elements: list[UIElement] = [*knobs, *leds, *inputs, *outputs]
    needs_layout = (
        any(el.x is None or el.y is None for el in all_elements)
        or assets.panel is None
        or assets.panel.x is None
        or assets.panel.y is None
    )

    if needs_layout:
        assets = layout_panel_assets(assets)

    module.assets = assets
    return module.assets
