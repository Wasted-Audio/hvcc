// -------------------------------------------------------------------
// Midi Input handler

void {{class_name}}::handleMidiInput(uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  // Midi events
  for (uint32_t i=0; i < midiEventCount; ++i)
  {
    int status = midiEvents[i].data[0];
    int command = status & 0xF0;
    int channel = status & 0x0F;
    int data1   = midiEvents[i].data[1];
    int data2   = midiEvents[i].data[2];

    // raw [midiin] messages
    int dataSize = *(&midiEvents[i].data + 1) - midiEvents[i].data;

    for (int i = 0; i < dataSize; ++i) {
      _context->sendMessageToReceiverV(HV_HASH_MIDIIN, 1000.0*midiEvents->frame/getSampleRate(), "ff",
        (float) midiEvents[i].data[i],
        (float) channel);
    }

    if(mrtSet.find(status) != mrtSet.end())
    {
      _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 1000.0*midiEvents->frame/getSampleRate(),
        "ff", (float) status);
    }

    // typical midi messages
    switch (command) {
      case 0x80: {  // note off
        _context->sendMessageToReceiverV(HV_HASH_NOTEIN, 1000.0*midiEvents->frame/getSampleRate(), "fff",
          (float) data1, // pitch
          (float) 0, // velocity
          (float) channel);
        break;
      }
      case 0x90: { // note on
        _context->sendMessageToReceiverV(HV_HASH_NOTEIN, 1000.0*midiEvents->frame/getSampleRate(), "fff",
          (float) data1, // pitch
          (float) data2, // velocity
          (float) channel);
        break;
      }
      case 0xA0: { // polyphonic aftertouch
        _context->sendMessageToReceiverV(HV_HASH_POLYTOUCHIN, 1000.0*midiEvents->frame/getSampleRate(), "fff",
          (float) data2, // pressure
          (float) data1, // note
          (float) channel);
        break;
      }
      case 0xB0: { // control change
        _context->sendMessageToReceiverV(HV_HASH_CTLIN, 1000.0*midiEvents->frame/getSampleRate(), "fff",
          (float) data2, // value
          (float) data1, // cc number
          (float) channel);
        break;
      }
      case 0xC0: { // program change
        _context->sendMessageToReceiverV(HV_HASH_PGMIN, 1000.0*midiEvents->frame/getSampleRate(), "ff",
          (float) data1,
          (float) channel);
        break;
      }
      case 0xD0: { // aftertouch
        _context->sendMessageToReceiverV(HV_HASH_TOUCHIN, 1000.0*midiEvents->frame/getSampleRate(), "ff",
          (float) data1,
          (float) channel);
        break;
      }
      case 0xE0: { // pitch bend
        // combine 7bit lsb and msb into 32bit int
        hv_uint32_t value = (((hv_uint32_t) data2) << 7) | ((hv_uint32_t) data1);
        _context->sendMessageToReceiverV(HV_HASH_BENDIN, 1000.0*midiEvents->frame/getSampleRate(), "ff",
          (float) value,
          (float) channel);
        break;
      }
      default: break;
    }
  }
}
