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

#include <stdio.h>
#include <mach/mach.h>
#include <stdlib.h>
#include "cpuid.h"
#include "Heavy_heavy.h"

void printHook(HeavyContextInterface *c, const char *name, const char *s, const HvMessage *m) {
  printf("[@ %.3f] %s: %s\n", hv_samplesToMilliseconds(c, hv_msg_getTimestamp(m)), name, s);
}

#define NUM_ITERATIONS 100000000 // 8388600
#define BLOCK_SIZE 512
#define SAMPLE_RATE 48000.0

int main(int argc, const char * argv[]) {
  cpuid_print_exts();

  HeavyContextInterface *context = hv_heavy_new(SAMPLE_RATE);
  hv_setPrintHook(context, &printHook);

  float *inputBuffers = (float *) malloc(hv_getNumInputChannels(context) * BLOCK_SIZE * sizeof(float));
  float *outputBuffers = (float *) malloc(hv_getNumOutputChannels(context) * BLOCK_SIZE * sizeof(float));

  mach_timebase_info_data_t sTimebaseInfo;
  mach_timebase_info(&sTimebaseInfo);
  uint64_t start = mach_absolute_time();
  for (int i = 0; i < NUM_ITERATIONS; ++i) {
    hv_processInline(context, inputBuffers, outputBuffers, BLOCK_SIZE);
  }
  uint64_t end = mach_absolute_time();
  uint64_t elapsedTimeNs = (end - start) * sTimebaseInfo.numer / sTimebaseInfo.denom;

  printf("Executed %i blocks of length %i at a sample rate of %gHz. A total of %llu samples were generated.\n",
      NUM_ITERATIONS, BLOCK_SIZE, SAMPLE_RATE, (1LLU*NUM_ITERATIONS) * BLOCK_SIZE);
  printf("Runtime is: %i iterations in %.3f seconds\n", NUM_ITERATIONS, elapsedTimeNs/1000000000.0);
  printf("  %f iterations/second.\n", (NUM_ITERATIONS*1000000000.0)/elapsedTimeNs);
  printf("  %.3f nanoseconds/block.\n", (1.0*elapsedTimeNs)/NUM_ITERATIONS);
  printf("  %0.6f%% CPU\n", 100.0*((elapsedTimeNs/1000000000.0)/NUM_ITERATIONS)/(BLOCK_SIZE/SAMPLE_RATE));

  free(inputBuffers);
  free(outputBuffers);

  hv_delete(context);

  return 0;
}
