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


import re
import json

from enum import Enum
from pathlib import Path


""" Vendored and modified from MicroNAM https://github.com/jaffco/MicroNAM
"""


class ModelNet(Enum):
    Nano = 1
    Feather = 2
    Lite = 3
    Standard = 4


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


def load_nam_file(nam_file: Path) -> tuple[ModelNet, int, list[float]]:
    with nam_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if "weights" not in payload.keys() or not isinstance(payload["weights"], list):
        raise ValueError("Input .nam file must contain a 'weights' array")

    weights = payload["weights"]
    for idx, value in enumerate(weights):
        if not isinstance(value, (int, float)):
            raise ValueError(f"weights[{idx}] is not numeric")

    weights_len = len(weights)

    if weights_len == 842:
        model_net = ModelNet.Nano
    elif weights_len == 3026:
        model_net = ModelNet.Feather
    elif weights_len == 6554:
        model_net = ModelNet.Lite
    elif weights_len == 13802:
        model_net = ModelNet.Standard
    else:
        raise ValueError(f"Invalid weights length: {weights_len}")

    return model_net, weights_len, weights


def convert_nam_to_header(nam_file: Path) -> str:
    symbol_stem = to_symbol_stem(nam_file)
    count_name = f"{symbol_stem}WeightsCount"
    weights_name = f"{symbol_stem}Weights"

    _, weights_len, weights = load_nam_file(nam_file)

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
