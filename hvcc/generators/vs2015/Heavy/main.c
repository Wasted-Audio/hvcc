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

#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "../../vs2015/Heavy/generated/c/Heavy_heavy.h"

void printHook(double timestampMs, const char *name, const char *s, void *userData) {
  printf("[@ %.3fms] %s: %s\n", timestampMs, name, s);
}

#define NUM_ITERATIONS 8388600
#define BLOCK_SIZE 512
#define SAMPLE_RATE 48000.0

int main(int argc, const char * argv[]) {
  Hv_heavy *context = hv_heavy_new(SAMPLE_RATE);
  hv_setPrintHook(context, &printHook);

  float *inputBuffers = (float *) malloc(hv_getNumInputChannels(context) * BLOCK_SIZE * sizeof(float));
  float *outputBuffers = (float *) malloc(hv_getNumOutputChannels(context) * BLOCK_SIZE * sizeof(float));

  uint64_t freq, start, end;
  QueryPerformanceFrequency((LARGE_INTEGER *) &freq);
  QueryPerformanceCounter((LARGE_INTEGER *) &start);
  for (int i = 0; i < NUM_ITERATIONS; ++i) {
    hv_heavy_process_inline(context, inputBuffers, outputBuffers, BLOCK_SIZE);
  }
  QueryPerformanceCounter((LARGE_INTEGER *) &end);

  const double elapsedTimeUs = 1000.0 * (end - start) / ((double) freq);
  printf("Executed %i blocks of length %i at a sample rate of %gHz. A total of %i samples were generated.\n",
      NUM_ITERATIONS, BLOCK_SIZE, SAMPLE_RATE, (int) (NUM_ITERATIONS * BLOCK_SIZE));
  printf("Runtime is: %i iterations in %.3f milliseconds\n", NUM_ITERATIONS, elapsedTimeUs);
  printf("  %f iterations/second.\n", (NUM_ITERATIONS*1000.0)/elapsedTimeUs);
  printf("  %.6f milliseconds per block.\n", elapsedTimeUs/NUM_ITERATIONS);
  printf("  %.6f microseconds per block.\n", 1000.0*elapsedTimeUs/NUM_ITERATIONS);
  printf("  %0.6f%% CPU\n", 100.0*((elapsedTimeUs/1000.0)/NUM_ITERATIONS)/(BLOCK_SIZE/SAMPLE_RATE));

  free(inputBuffers);
  free(outputBuffers);

  hv_heavy_free(context);

  Sleep(10000);

  return 0;
}
