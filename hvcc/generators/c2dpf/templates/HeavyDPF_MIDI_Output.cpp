// -------------------------------------------------------------------
// Midi Send handler

void {{class_name}}::handleMidiSend(uint32_t sendHash, const HvMessage *m)
{
  MidiEvent midiSendEvent;
  midiSendEvent.frame = 0;
  midiSendEvent.dataExt = nullptr;

  switch(sendHash){
    case HV_HASH_NOTEOUT: // __hv_noteout
    {
      uint8_t note = hv_msg_getFloat(m, 0);
      uint8_t velocity = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      ch %= 16;  // drop any pd "ports"

      midiSendEvent.size = 3;
      if (velocity > 0){
        midiSendEvent.data[0] = 0x90 | ch; // noteon
      } else {
        midiSendEvent.data[0] = 0x80 | ch; // noteoff
      }
      midiSendEvent.data[1] = note;
      midiSendEvent.data[2] = velocity;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_CTLOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t cc = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      ch %= 16;

      midiSendEvent.size = 3;
      midiSendEvent.data[0] = 0xB0 | ch; // send CC
      midiSendEvent.data[1] = cc;
      midiSendEvent.data[2] = value;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_POLYTOUCHOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t note = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);

      midiSendEvent.size = 3;
      midiSendEvent.data[0] = 0xA0 | ch; // send Poly Aftertouch
      midiSendEvent.data[1] = note;
      midiSendEvent.data[2] = value;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_PGMOUT:
    {
      uint8_t pgm = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      midiSendEvent.size = 2;
      midiSendEvent.data[0] = 0xC0 | ch; // send Program Change
      midiSendEvent.data[1] = pgm;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_TOUCHOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      midiSendEvent.size = 2;
      midiSendEvent.data[0] = 0xD0 | ch; // send Touch
      midiSendEvent.data[1] = value;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_BENDOUT:
    {
      uint16_t value = hv_msg_getFloat(m, 0);
      uint8_t lsb  = value & 0x7F;
      uint8_t msb  = (value >> 7) & 0x7F;
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      midiSendEvent.size = 3;
      midiSendEvent.data[0] = 0xE0 | ch; // send Bend
      midiSendEvent.data[1] = lsb;
      midiSendEvent.data[2] = msb;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_MIDIOUT: // __hv_midiout
    {
      const uint8_t numElements = m->numElements;
      if (numElements <=4 )
      {
        for (int i = 0; i < numElements; ++i)
        {
          midiSendEvent.data[i] = hv_msg_getFloat(m, i);
        }
      }
      else
      {
        printf("> we do not support sysex yet \n");
        break;
      }

      // unsigned char* rawData = new unsigned char;
      // for (int i = 0; i < numElements; ++i) {
      //   rawData[i] = (uint8_t) hv_msg_getFloat(m, i);
      //   printf("> data: %d \n", rawData[i]);
      // }

      midiSendEvent.size = numElements;
      // midiSendEvent.dataExt = (const uint8_t *) rawData;

      writeMidiEvent(midiSendEvent);
      break;
    }
    default:
      break;
  }
}
