/**
 * Copyright (C) 2026 Wasted Audio
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "HvUtils.h"
#include "Heavy_heavy.h"
#include "tinywav.h"

// deterministic test input, exactly representable as float
static float input_sample(int channel, int n) {
  return (float) ((n * (2 * channel + 3)) % 1009 - 504) / 512.0f;
}

// $ heavy out.wav sampleRate blockSize numIterations offset inPlace
// offset: shift both buffers by this many floats (1 makes them misaligned for SSE/AVX)
// inPlace: use the same buffer for input and output
int main(int argc, const char *argv[]) {
  if (argc < 7) return -1;
  const char *outputPath = argv[1];
  const double sampleRate = atof(argv[2]);
  const int blockSize = atoi(argv[3]);
  const int numIterations = atoi(argv[4]);
  const int offset = atoi(argv[5]);
  const int inPlace = atoi(argv[6]);

  HeavyContextInterface *context = hv_heavy_new(sampleRate);
  const int numIn = hv_getNumInputChannels(context);
  const int numOut = hv_getNumOutputChannels(context);
  const int numMax = numIn > numOut ? numIn : numOut;
  hv_assert(!inPlace || numIn == numOut);

  TinyWav tw;
  tinywav_open_write(&tw, numOut, (int32_t) hv_getSampleRate(context), TW_FLOAT32, TW_INTERLEAVED, outputPath);

  // allocate a multiple of 32 bytes (aligned_alloc), with room for the offset
  const size_t numFloats = ((size_t) (numMax * blockSize + offset) + 7) & ~(size_t) 7;
  float *inMem = (float *) hv_malloc(numFloats * sizeof(float));
  float *outMem = (float *) hv_malloc(numFloats * sizeof(float));
  float *in = inMem + offset;
  float *out = inPlace ? in : outMem + offset;

  for (int k = 0; k < numIterations; ++k) {
    for (int j = 0; j < blockSize; ++j) {
      for (int c = 0; c < numIn; ++c) in[j * numIn + c] = input_sample(c, k * blockSize + j);
    }
    hv_processInlineInterleaved(context, in, out, blockSize);
    tinywav_write_f(&tw, out, blockSize);
  }

  tinywav_close_write(&tw);
  hv_heavy_free(context);
  hv_free(inMem);
  hv_free(outMem);
  return 0;
}
