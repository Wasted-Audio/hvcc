# MIT License
#
# Copyright (c) 2026 Jaffx Audio Inc.
# Copyright (c) 2026 Wasted Audio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
import re
from enum import Enum
from pathlib import Path

""" Vendored and modified from MicroNAM https://github.com/jaffco/MicroNAM
"""


class ModelNet(Enum):
    Nano = 1
    Feather = 2
    Lite = 3
    Standard = 4
    A2Lite = 5
    A2Full = 6


def to_symbol_stem(nam_path: Path) -> str:
    stem = nam_path.stem.strip()
    if not stem:
        return "NamModel"

    # Split on non-alphanumeric boundaries, then form PascalCase.
    raw_parts = [p for p in re.split(r"[^A-Za-z0-9]+", stem) if p]
    if not raw_parts:
        return "NamModel"

    parts = []
    for part in raw_parts:
        if part[0].isdigit():
            part = f"M{part}"
        parts.append(part[0].upper() + part[1:])

    return "".join(parts)


def format_float(value: float) -> str:
    # Keep enough precision for model weights while staying compact.
    return f"{format(value, '.17g')}f"


def load_nam_file(nam_file: Path, size: str | None = None) -> tuple[ModelNet, int, list[float]]:
    if size is not None and size not in ("lite", "full"):
        raise ValueError(f"Invalid size: {size}, expected 'lite', 'full' or None")

    with nam_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if payload.get("weights") is not None and \
        isinstance(payload.get("weights"), list) and \
        payload['weights']:

        weights = payload['weights']

        weights_len = len(weights)

        if weights_len == 842:
            model_net = ModelNet.Nano
        elif weights_len == 3026:
            model_net = ModelNet.Feather
        elif weights_len == 6554:
            model_net = ModelNet.Lite
        elif weights_len == 13802:
            model_net = ModelNet.Standard
        elif weights_len == 1871:
            model_net = ModelNet.A2Lite
        elif weights_len == 12146:
            model_net = ModelNet.A2Full
        else:
            raise ValueError(f"Invalid weights length: {weights_len}")

        return model_net, weights_len, weights

    config = payload.get("config")
    submodules = config.get("submodels") if config else None

    if not isinstance(submodules, list):
        raise TypeError("Invalid or missing submodules in config")

    # Without a size, use the highest quality submodel: that is how the exporter
    # orders them, by max_value. Sizing the loop down to that one submodel lets
    # the loop below do the matching, instead of duplicating it.
    if size is None:
        best = None
        for sub in submodules:
            if best is None or sub.get("max_value", -1) > best.get("max_value", -1):
                best = sub
        if best is None:
            raise ValueError("No submodules in config")
        submodules = [best]

    for sub in submodules:
        if sub.get("model") is None:
            continue

        model = sub["model"]
        model_config = model.get("config")
        if not model_config:
            continue
        if "layers" not in model_config or not isinstance(model_config["layers"], list) \
            or not model_config["layers"]:
            continue

        layers = model_config["layers"]
        channels = layers[0]["channels"]

        is_lite = channels == 3
        is_full = channels == 8

        # Submodels that are not A2 wave-nets are skipped: a container can hold
        # other architectures next to the ones we want.
        if not is_lite and not is_full:
            continue

        if size == "lite" and not is_lite:
            continue
        if size == "full" and not is_full:
            continue

        model_net = ModelNet.A2Lite if is_lite else ModelNet.A2Full

        # The weights are on the submodel's model, not on the submodel itself.
        weights = model.get("weights")
        if not weights:
            raise ValueError(f"Submodel with {channels} channels has no weights")

        weights_len = len(weights)
        expected_len = 1871 if is_lite else 12146
        if weights_len != expected_len:
            raise ValueError(f"Invalid weights length: {weights_len}, expected: {expected_len}")

        return model_net, weights_len, weights

    if size is None:
        raise ValueError("No A2 lite or full submodel in config")
    raise ValueError(f"No '{size}' submodel in config")


def convert_nam_to_header(nam_file: Path, size: str | None = None) -> str:
    symbol_stem = to_symbol_stem(nam_file)
    count_name = f"{symbol_stem}{size or ''}WeightsCount"
    weights_name = f"{symbol_stem}{size or ''}Weights"

    _, weights_len, weights = load_nam_file(nam_file, size=size)

    lines = [
        "#pragma once",
        "",
        f"static const unsigned int {count_name} = {weights_len};",
        f"static const float {weights_name}[{count_name}] = {{",
    ]

    row = []
    for idx, value in enumerate(weights, start=1):
        row.append(format_float(float(value)))
        if idx % 6 == 0:
            lines.append("    " + ", ".join(row) + ",")
            row = []

    if row:
        lines.append("    " + ", ".join(row) + ",")

    lines.append("};")
    lines.append("")

    return "\n".join(lines)
