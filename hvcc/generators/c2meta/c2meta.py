# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import shutil
import time
from pathlib import Path

import jinja2
from PIL import Image
from pydantic import BaseModel

from hvcc.generators.copyright import copyright_manager
from hvcc.generators.filters import filter_uniqueid
from hvcc.interpreters.pd2hv.NotificationEnum import NotificationEnum
from hvcc.types.compiler import CompilerMsg, CompilerNotif, CompilerResp, ExternInfo, Generator
from hvcc.types.meta import Meta
from hvcc.types.metamodule import Assets, UIElement

from .panel_val import ensure_panel_assets


class mmJson(BaseModel):
    MetaModulePluginMaintainer: str
    MetaModulePluginMaintainerEmail: str
    MetaModulePluginMaintainerUrl: str
    MetaModuleDescription: str



def write_asset_files(assets: Assets, out_dir: Path) -> None:
    """Copy the panel image and all component images into out_dir/assets."""
    asset_dir = out_dir / "assets"
    components_dir = asset_dir / "components"
    components_dir.mkdir(parents=True, exist_ok=True)

    assert assets.panel

    # Panel image: generate directly in assets/ or copy custom image
    if assets.panel.image is None:
        panel_path = asset_dir / "panel.png"
        color = assets.panel.color.as_rgb_tuple() if assets.panel.color else (60, 60, 60)
        assert assets.panel.x is not None and assets.panel.y is not None
        panel_img = Image.new("RGBA", (assets.panel.x, assets.panel.y), color)
        panel_img.save(panel_path)
        assets.panel.image = panel_path
    elif assets.panel.image.parent != asset_dir:
        dest_panel = asset_dir / assets.panel.image.name
        shutil.copyfile(assets.panel.image, dest_panel)
        assets.panel.image = dest_panel

    # Components: copy unique component images into assets/components/
    elements: list[UIElement] = [*assets.knobs, *assets.leds, *assets.inputs, *assets.outputs]
    for img_path in {el.image for el in elements}:
        shutil.copyfile(img_path, components_dir / img_path.name)


def write_screenshot(assets, screenshot_path: Path) -> None:
    """Render a visual composite of the panel and placed components."""
    if not (assets.panel and assets.panel.image and assets.panel.image.exists()):
        return

    with Image.open(assets.panel.image).convert('RGBA') as screenshot:
        elements: list[UIElement] = [*assets.knobs, *assets.leds, *assets.inputs, *assets.outputs]
        for element in elements:
            if element.x is None or element.y is None:
                continue
            with Image.open(element.image) as img:
                screenshot.alpha_composite(img, (element.x, element.y))

        screenshot.save(screenshot_path)


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
        patch_meta: Meta,
        num_input_channels: int = 0,
        num_output_channels: int = 0,
        copyright: str | None = None,
        verbose: bool | None = False
    ) -> CompilerResp:

        tick = time.time()
        patch_meta = patch_meta or Meta()

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

            # plan layout and resolve assets
            assets = ensure_panel_assets(mm_meta, externs, num_input_channels, num_output_channels, verbose)

            # write runtime assets for plugin
            write_asset_files(assets, out_dir)

            # generate screenshot preview
            write_screenshot(assets, out_dir / "screenshot.png")

            # generate elements.cpp
            elements_cpp = Path(source_dir, f"{patch_name.lower()}_elements.cpp")
            with open(elements_cpp, "w") as f:
                f.write(env.get_template("elements.cpp").render(
                    name=patch_name,
                    meta=mm_meta,
                    num_input_channels=num_input_channels,
                    num_output_channels=num_output_channels,
                    receivers=receiver_list,
                    senders=sender_list,
                    copyright=copyright_c))

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

        except Exception as e:  # noqa: BLE001
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
