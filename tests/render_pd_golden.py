# Copyright (C) 2022 Wasted Audio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Render a signal test patch with Pd vanilla to a golden WAV file.

The patch's [dac~] is replaced by [tabwrite~]s in a temporary copy, which record
exactly as many samples as the signal tests render with heavy
(48 kHz, 100 blocks of 480 samples by default). The golden file is written next
to the patch as <name>.golden.wav (32 bit float).

    python tests/render_pd_golden.py tests/pd/signal/test-delread4.pd --pd /path/to/pd
"""

import argparse
import os
import re
import shutil
import subprocess
import tempfile

import numpy
from scipy.io import wavfile


def render(pd_path: str, pd_bin: str, sample_rate: int, num_samples: int) -> str:
    with open(pd_path) as f:
        lines = f.read().split(";\n")
    out_dir = tempfile.mkdtemp()
    wav = os.path.join(out_dir, "out.wav")
    # top-level object index of each line (subpatches count as one object)
    depth, index, nch, first_conn = 0, -1, 0, None
    for i, line in enumerate(lines):
        if line.startswith("#N canvas"):
            if depth == 1:
                index += 1
            depth += 1
        elif line.startswith("#X restore"):
            depth -= 1
        elif depth == 1 and first_conn is None and line.startswith("#X connect"):
            first_conn = i
        elif depth == 1 and re.match(r"#X (obj|msg|floatatom|symbolatom|text|listbox) ", line):
            index += 1
            m = re.match(r"#X obj (-?\d+) (-?\d+) dac~(.*)", line)
            if m:
                assert nch == 0, "only one [dac~] is supported"
                nch = len(m.group(3).split()) or 2
                # replace [dac~] by a subpatch with one inlet~ -> [tabwrite~] per channel
                tabs = [f"hvgolden-ch{c}" for c in range(nch)]
                rec = ["#N canvas 0 22 450 300 rec 0"]
                for c, t in enumerate(tabs):
                    rec += [f"#X obj {10 + 100 * c} 10 inlet~", f"#X obj {10 + 100 * c} 70 tabwrite~ {t}",
                            f"#X obj {10 + 100 * c} 100 table {t} {num_samples}"]
                rec += ["#X obj 10 40 r hvgolden-start", "#X obj 10 130 r hvgolden-write",
                        f"#X msg 10 160 write -bytes 4 {wav} {' '.join(tabs)}", "#X obj 10 190 soundfiler"]
                k = 3 * nch
                rec += [f"#X connect {3 * c} 0 {3 * c + 1} 0" for c in range(nch)]
                rec += [f"#X connect {k} 0 {3 * c + 1} 0" for c in range(nch)]
                rec += [f"#X connect {k + 1} 0 {k + 2} 0", f"#X connect {k + 2} 0 {k + 3} 0",
                        f"#X restore {m.group(1)} {m.group(2)} pd rec"]
                lines[i] = ";\n".join(rec)
    assert nch > 0, "no [dac~] in the patch"
    n = index + 1
    # recording starts with the first DSP block; tables hold exactly num_samples
    dur_ms = 1000.0 * (num_samples + 64) / sample_rate
    extra = [
        "#X obj 600 10 loadbang",
        "#X msg 600 40 \\; pd dsp 1 \\; hvgolden-start bang",
        f"#X obj 700 40 del {dur_ms}",
        "#X msg 700 70 \\; hvgolden-write bang \\; pd quit",
        f"#X connect {n} 0 {n + 1} 0",
        f"#X connect {n} 0 {n + 2} 0",
        f"#X connect {n + 2} 0 {n + 3} 0",
    ]
    # insert the extra objects before the first top-level connect line
    first_conn = len(lines) if first_conn is None else first_conn
    body = [x for x in lines[:first_conn] + extra[:4] + lines[first_conn:] + extra[4:] if x.strip()]
    tmp = os.path.join(out_dir, os.path.basename(pd_path))
    with open(tmp, "w") as f:
        f.write(";\n".join(body) + ";\n")
    subprocess.run([pd_bin, "-nogui", "-noaudio", "-batch", "-r", str(sample_rate), tmp],
                   check=True, capture_output=True, timeout=60)
    _, data = wavfile.read(wav)
    assert len(data) == num_samples, f"Pd rendered {len(data)} samples instead of {num_samples}"
    golden = os.path.splitext(pd_path)[0] + ".golden.wav"
    wavfile.write(golden, sample_rate, numpy.ascontiguousarray(data, dtype=numpy.float32))
    shutil.rmtree(out_dir)
    return golden


def main():
    parser = argparse.ArgumentParser(description="Render golden files for signal tests with Pd vanilla.")
    parser.add_argument("pd_path", nargs="+", help="Pd test patch(es) containing one [dac~].")
    parser.add_argument("--pd", default=shutil.which("pd") or "pd", help="Pd binary.")
    parser.add_argument("--samplerate", "-r", type=int, default=48000)
    parser.add_argument("--samples", "-n", type=int, default=48000, help="Defaults to 100 blocks of 480.")
    args = parser.parse_args()
    for p in args.pd_path:
        print(render(p, args.pd, args.samplerate, args.samples))


if __name__ == "__main__":
    main()
