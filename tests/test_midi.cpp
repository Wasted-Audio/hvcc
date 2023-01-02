/**
 * Copyright (C) 2014-2018 Enzien Audio, Ltd.
 * Copyright (C) 2022 Wasted Audio
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
#include <set>

// #include "Options.h"
#include "MidiFile.h"
#include "Heavy_heavy.h"
#include "Heavy_heavy.hpp"

#define BLOCK_SIZE 1024

#define HV_HASH_NOTEIN          0x67E37CA3
#define HV_HASH_CTLIN           0x41BE0f9C
#define HV_HASH_POLYTOUCHIN     0xBC530F59
#define HV_HASH_PGMIN           0x2E1EA03D
#define HV_HASH_TOUCHIN         0x553925BD
#define HV_HASH_BENDIN          0x3083F0F7
#define HV_HASH_MIDIIN          0x149631bE
#define HV_HASH_MIDIREALTIMEIN  0x6FFF0BCF

#define HV_HASH_NOTEOUT         0xD1D4AC2
#define HV_HASH_CTLOUT          0xE5e2A040
#define HV_HASH_POLYTOUCHOUT    0xD5ACA9D1
#define HV_HASH_PGMOUT          0x8753E39E
#define HV_HASH_TOUCHOUT        0x476D4387
#define HV_HASH_BENDOUT         0xE8458013
#define HV_HASH_MIDIOUT         0x6511DE55
#define HV_HASH_MIDIOUTPORT     0x165707E4

#define MIDI_RT_CLOCK           0xF8
#define MIDI_RT_START           0xFA
#define MIDI_RT_CONTINUE        0xFB
#define MIDI_RT_STOP            0xFC
#define MIDI_RT_ACTIVESENSE     0xFE
#define MIDI_RT_RESET           0xFF

// midi realtime messages
std::set<int> mrtSet {
  MIDI_RT_CLOCK,
  MIDI_RT_START,
  MIDI_RT_CONTINUE,
  MIDI_RT_STOP,
  MIDI_RT_RESET
};

using namespace std;
using namespace smf;

void printHook(HeavyContextInterface *c, const char *name, const char *s, const HvMessage *m) {
  printf("[@ %.3f] %s: %s\n", hv_samplesToMilliseconds(c, hv_msg_getTimestamp(m)), name, s);
}

int main(int argc, const char *argv[]) {
  // Options options;
  MidiFile midifile;
  // if (options.getArgCount() > 1) midifile.read(options.getArg(2));
  // else midifile.read(std::cin);

  midifile.read(argv[1]);

  // const int numIterations = (argc > 1) ? atoi(argv[1]) : 1;
  const int numIterations = 1;

  const int numOutputChannels = 2;
  HeavyContextInterface *context = hv_heavy_new_with_options(48000.0, 10, 11, 0);
  // HeavyContextInterface *context = hv_heavy_new(48000.0);
  hv_setPrintHook(context, &printHook);

  MidiEvent* mev;

  float *outBuffers = (float *) malloc(numOutputChannels * BLOCK_SIZE * sizeof(float));

  for (int i = 0; i < numIterations; ++i) {
    for (int event=0; event < midifile[0].size(); event++) {
      // std::cout << midifile[0].size();
      mev = &midifile[0][event];

      int status = (int)(*mev)[0];
      int command = status & 0xf0;
      int channel = status & 0x0f;
      int data1 = (int)(*mev)[1];
      int data2 = (int)(*mev)[2];
      
      // realtime messages
      if(mrtSet.find(status) != mrtSet.end())
      {
        context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0, "ff", 
        (float) status);
      }

      switch (command) {
        case 0x80: {  // note off
          context->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
            (float) data1, // pitch
            (float) 0, // velocity
            (float) channel);
          break;
        }
        case 0x90: { // note on
          context->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
            (float) data1, // pitch
            (float) data2, // velocity
            (float) channel);
          break;
        }
        case 0xA0: { // polyphonic aftertouch
          context->sendMessageToReceiverV(HV_HASH_POLYTOUCHIN, 0, "fff",
            (float) data2, // pressure
            (float) data1, // note
            (float) channel);
          break;
        }
        case 0xB0: { // control change
          context->sendMessageToReceiverV(HV_HASH_CTLIN, 0, "fff",
            (float) data2, // value
            (float) data1, // cc number
            (float) channel);
          break;
        }
        case 0xC0: { // program change
          context->sendMessageToReceiverV(HV_HASH_PGMIN, 0, "ff",
            (float) data1,
            (float) channel);
          break;
        }
        case 0xD0: { // aftertouch
          context->sendMessageToReceiverV(HV_HASH_TOUCHIN, 0, "ff",
            (float) data1, // pressure
            (float) channel);
          break;
        }
        case 0xE0: { // pitch bend
          // combine 7bit lsb and msb into 32bit int
          hv_uint32_t value = (((hv_uint32_t) data2) << 7) | ((hv_uint32_t) data1);
          context->sendMessageToReceiverV(HV_HASH_BENDIN, 0, "ff",
            (float) value, // bend
            (float) channel);
          break;
        }
        default: break;
      }
    }

    hv_processInline(context, NULL, outBuffers, BLOCK_SIZE);
  }

  hv_delete(context);
  free(outBuffers);
  return 0;
}
