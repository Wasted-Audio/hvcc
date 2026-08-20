# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import shutil
import tempfile
import time
import jinja2

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from PIL import Image

from hvcc.generators.copyright import copyright_manager
from hvcc.generators.filters import filter_uniqueid

from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import Generator, CompilerResp, CompilerMsg, CompilerNotif, ExternInfo
from hvcc.types.meta import Meta, MetaModule

from .meta_types import Knob, Input, Output, Led, Assets, UIElement
from .panel import layout_panel_assets


class mmJson(BaseModel):
    MetaModulePluginMaintainer: str
    MetaModulePluginMaintainerEmail: str
    MetaModulePluginMaintainerUrl: str
    MetaModuleDescription: str


def ensure_panel_assets(
    mm_meta: MetaModule,
    externs: ExternInfo,
    num_input_channels: int,
    num_output_channels: int,
    tmp_dir: Path,
    verbose: Optional[bool] = False
) -> Assets:
    """Return the module's assets, generating a default panel if none exist."""
    module = mm_meta.modules[0]

    if module.assets is not None and \
            module.assets.panel is not None and \
            module.assets.panel.image is not None and \
            module.assets.panel.size is not None:
        return module.assets

    if verbose:
        print("--> c2meta: generating custom panel")

    assets = Assets(
        panel=module.assets.panel if module.assets is not None else None,
        knobs=[Knob(param=p.display) for _, p in externs.parameters.inParam],
        inputs=[Input(id=i) for i in range(num_input_channels)],
        outputs=[Output(id=i) for i in range(num_output_channels)],
        leds=[
            Led(led=p.display)
            for _, p in externs.parameters.outParam
            if p.display is not None
        ],
    )
    panel_assets = layout_panel_assets(assets)

    assert panel_assets.panel and panel_assets.panel.size and panel_assets.panel.color
    panel_img = Image.new(
        "RGBA",
        (panel_assets.panel.size.x, panel_assets.panel.size.y),
        panel_assets.panel.color.as_rgb_tuple(),
    )

    panel_path = tmp_dir / "panel.png"
    panel_img.save(panel_path)
    panel_assets.panel.image = panel_path

    module.assets = panel_assets
    return module.assets


def write_asset_files(assets: Assets, out_dir: Path) -> None:
    """Copy the panel image and all component images into out_dir/assets."""
    asset_dir = out_dir / "assets"
    components_dir = asset_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    assert assets.panel and assets.panel.image
    shutil.copyfile(assets.panel.image, asset_dir / "panel.png")

    screenshot = Image.open(assets.panel.image)

    elements: list[UIElement] = [*assets.knobs, *assets.leds, *assets.inputs, *assets.outputs]
    for element in elements:
        shutil.copyfile(element.image, components_dir / element.image.name)

        assert element.coords
        img = Image.open(element.image)
        screenshot.alpha_composite(img, (element.coords.x, element.coords.y))

    screenshot.save(out_dir / "screenshot.png")


class c2meta(Generator):
    """ Generates a Meta wrapper for a given patch.
    """

    @classmethod
    def compile(
        cls,
        c_src_dir: Path,
        out_dir: Path,
        externs: ExternInfo,
        patch_name: str,
        patch_meta: Meta = Meta(),
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: Optional[str] = None,
        verbose: Optional[bool] = False
    ) -> CompilerResp:

        tick = time.time()

        out_dir = Path(out_dir, "plugin")
        receiver_list = externs.parameters.inParam
        sender_list = externs.parameters.outParam

        mm_meta = patch_meta.meta

        copyright_c = copyright_manager.get_copyright_for_c(copyright)

        try:
            # ensure that the output directory does not exist
            out_dir = out_dir.absolute()
            if out_dir.exists():
                shutil.rmtree(out_dir)

            # copy over static files
            shutil.copytree(Path(Path(__file__).parent, "static"), out_dir)

            # copy over generated C source files
            source_dir = Path(out_dir, "source")
            shutil.copytree(c_src_dir, source_dir)

            # initialize the jinja template environment
            env = jinja2.Environment()
            env.filters["uniqueid"] = filter_uniqueid

            env.loader = jinja2.FileSystemLoader(
                Path(Path(__file__).parent, "templates"))

            # generate Meta wrapper from template
            mm_h_path = Path(source_dir, f"HeavyMetaModule_{patch_name}.hpp")
            with open(mm_h_path, "w") as f:
                f.write(env.get_template("HeavyMetaModule.hpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    class_name=f"HeavyMetaModule_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))

            # generate Meta wrapper from template
            mm_c_path = Path(source_dir, f"HeavyMetaModule_{patch_name}.cpp")
            with open(mm_c_path, "w") as f:
                f.write(env.get_template("HeavyMetaModule.cpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    class_name=f"HeavyMetaModule_{patch_name}",
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))

            # generate plugin.cpp
            plugin_cpp = Path(source_dir, "plugin.cpp")
            with open(plugin_cpp, "w") as f:
                f.write(env.get_template("plugin.cpp").render(
                    name=patch_name
                ))

            # generate panel assets
            with tempfile.TemporaryDirectory() as tmp_dir:
                assets = ensure_panel_assets(
                    mm_meta, externs, num_input_channels, num_output_channels, Path(tmp_dir), verbose
                )
                write_asset_files(assets, out_dir)

            # generate elements.cpp
            elements_cpp = Path(source_dir, f"{patch_name.lower()}_elements.cpp")
            with open(elements_cpp, "w") as f:
                f.write(env.get_template("elements.cpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list
                ))

            # generate plugin CMakeLists.txt
            mm_cmake_path = Path(out_dir, "CMakeLists.txt")
            with open(mm_cmake_path, "w") as f:
                f.write(env.get_template("CMakeLists.txt").render(
                    name=patch_name,
                    meta=mm_meta))

            # generate root CMakeLists.txt
            root_cmake_path = Path(out_dir, "../CMakeLists.txt")
            with open(root_cmake_path, "w") as f:
                f.write(env.get_template("CMakeLists_root.txt").render(
                    name=patch_name,
                    meta=mm_meta))

            plugin_json_path = Path(out_dir, "plugin.json")
            plugin_json = mm_meta.model_copy(deep=True)

            # drop additional metadata
            plugin_json.sdk_path = None
            plugin_json.modules[0].assets = None

            with open(plugin_json_path, "w") as f:
                f.write(plugin_json.model_dump_json(indent=4, exclude_none=True))


            mm_json_path = Path(out_dir, "plugin-mm.json")
            mm_json = mmJson(
                MetaModulePluginMaintainer="Wasted Audio",
                MetaModulePluginMaintainerEmail="developer@wasted.audio",
                MetaModulePluginMaintainerUrl="https://wasted.audio",
                MetaModuleDescription=mm_meta.description
            )

            with open(mm_json_path, "w") as f:
                f.write(mm_json.model_dump_json(indent=4))

            return CompilerResp(
                stage="c2meta",
                in_dir=c_src_dir,
                out_dir=out_dir,
                out_file=mm_h_path.absolute().parent,
                compile_time=time.time() - tick
            )

        except Exception as e:
            return CompilerResp(
                stage="c2meta",
                notifs=CompilerNotif(
                    has_error=True,
                    exception=e,
                    warnings=[],
                    errors=[CompilerMsg(
                        enum=NotificationEnum.ERROR_EXCEPTION,
                        message=str(e)
                    )]
                ),
                in_dir=c_src_dir,
                out_dir=out_dir,
                compile_time=time.time() - tick
            )
