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

#include "Heavy_heavy.h"

#define BLOCK_SIZE 1024

void printHook(HeavyContextInterface *c, const char *name, const char *s, const HvMessage *m) {
  printf("[@ %.3f] %s: %s\n", hv_samplesToMilliseconds(c, hv_msg_getTimestamp(m)), name, s);
}

int main(int argc, const char *argv[]) {
  const int numIterations = (argc > 1) ? atoi(argv[1]) : 1;

  const int numOutputChannels = 2;
  HeavyContextInterface *context = hv_heavy_new(48000.0);
  hv_setPrintHook(context, &printHook);

  float *outBuffers = (float *) malloc(numOutputChannels * BLOCK_SIZE * sizeof(float));

  for (int i = 0; i < numIterations; ++i) {
    hv_processInline(context, NULL, outBuffers, BLOCK_SIZE);
  }

  hv_delete(context);
  free(outBuffers);
  return 0;
}
