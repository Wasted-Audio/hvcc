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
#include <stdlib.h>
#include <sys/time.h>
#include "Heavy_heavy.h"
#include "HvUtils.h"

static void timeval_subtract(struct timeval *result, struct timeval *end, struct timeval *start) {
  if (end->tv_usec < start->tv_usec) {
    result->tv_sec = end->tv_sec - start->tv_sec - 1;
    result->tv_usec = 1000000L + end->tv_usec - start->tv_usec;
  } else {
    result->tv_sec = end->tv_sec - start->tv_sec;
    result->tv_usec = end->tv_usec - start->tv_usec;
  }
}

int main(int argc, const char *argv[]) {
  if (argc != 4) return -1;

  const double sampleRate = atof(argv[1]);
  const int blockSize = atoi(argv[2]);
  const int numIterations = atoi(argv[3]);

  HeavyContextInterface *context = hv_heavy_new(sampleRate);

  float *inBuffers = (float *) hv_malloc(hv_getNumInputChannels(context) * blockSize * sizeof(float));
  float *outBuffers = (float *) hv_malloc(hv_getNumOutputChannels(context) * blockSize * sizeof(float));

  struct timeval elapsed, start, end;
  gettimeofday(&start, NULL);
  for (int i = 0; i < numIterations; ++i) {
    hv_processInline(context, inBuffers, outBuffers, blockSize);
  }
  gettimeofday(&end, NULL);
  timeval_subtract(&elapsed, &end, &start);
  uint64_t elapsedTimeUs = (elapsed.tv_sec * 1000000L) + elapsed.tv_usec;

  // return the us per block
  printf("%f", elapsedTimeUs/((double) numIterations));

  hv_free(inBuffers);
  hv_free(outBuffers);
  hv_delete(context);

  return 0;
}
