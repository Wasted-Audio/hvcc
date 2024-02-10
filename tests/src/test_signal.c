/**
 * Copyright (C) 2014-2018 Enzien Audio, Ltd.
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

int main(int argc, const char *argv[]) {
  #if HV_SIMD_AVX
    printf("AVX!\n");
  #elif HV_SIMD_SSE
    printf("SSE!\n");
  #elif HV_SIMD_NEON
    printf("NEON!\n");
  #else // HV_SIMD_NONE
    printf("NONE!\n");
  #endif
  if (argc < 5) return -1;
  const char *outputPath = argv[1];
  const double sampleRate = atof(argv[2]);
  const int blockSize = atoi(argv[3]);
  const int numIterations = atoi(argv[4]);

  HeavyContextInterface *context = hv_heavy_new(sampleRate);

  // ensure that number of IO channels is correct
  hv_assert(hv_getNumInputChannels(context) == 0);
  hv_assert(
      hv_getNumOutputChannels(context) == 1 ||
      hv_getNumOutputChannels(context) == 2);

  TinyWav tw;
  tinywav_open_write(&tw,
      hv_getNumOutputChannels(context),
      (int32_t) hv_getSampleRate(context),
      TW_FLOAT32, TW_INLINE, outputPath);

  float *outBuffers = (float *) hv_malloc(
      hv_getNumOutputChannels(context) * blockSize * sizeof(float));

  for (int i = 0; i < numIterations; ++i) {
    hv_processInline(context, NULL, outBuffers, blockSize);

    // write buffer to output
    tinywav_write_f(&tw, outBuffers, blockSize);
  }

  tinywav_close_write(&tw);
  hv_heavy_free(context);
  free(outBuffers);
  return 0;
}
