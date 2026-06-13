void HandleMidiOut(uint8_t *midiData, const uint8_t numElements)
{
  for (int i = 0; i < numElements; i++) {
    midi_tx_fifo.PushBack(midiData[i]);
  }
}

void HandleMidiSend(uint32_t sendHash, const HvMessage *m)
{
  switch(sendHash){
    case HV_HASH_NOTEOUT: // __hv_noteout
    {
      uint8_t note = hv_msg_getFloat(m, 0);
      uint8_t velocity = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      ch %= 16;  // drop any pd "ports"

      const uint8_t numElements = 3;
      uint8_t midiData[numElements];

      if (velocity > 0){
        midiData[0] = 0x90 | ch; // noteon
      } else {
        midiData[0] = 0x80 | ch; // noteoff
      }
      midiData[1] = note;
      midiData[2] = velocity;

      HandleMidiOut(midiData, numElements);
      break;
    }
    case HV_HASH_POLYTOUCHOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t note = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      ch %= 16; // drop any pd "ports"

      const uint8_t numElements = 3;
      uint8_t midiData[numElements];
      midiData[0] = 0xA0 | ch; // send Poly Aftertouch
      midiData[1] = note;
      midiData[2] = value;

      HandleMidiOut(midiData, numElements);
      break;
    }
    case HV_HASH_CTLOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t cc = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      ch %= 16;

      const uint8_t numElements = 3;
      uint8_t midiData[numElements];
      midiData[0] = 0xB0 | ch; // send CC
      midiData[1] = cc;
      midiData[2] = value;

      HandleMidiOut(midiData, numElements);
      break;
    }
    case HV_HASH_PGMOUT:
    {
      uint8_t pgm = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      const uint8_t numElements = 2;
      uint8_t midiData[numElements];
      midiData[0] = 0xC0 | ch; // send Program Change
      midiData[1] = pgm;

      HandleMidiOut(midiData, numElements);
      break;
    }
    case HV_HASH_TOUCHOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      const uint8_t numElements = 2;
      uint8_t midiData[numElements];
      midiData[0] = 0xD0 | ch; // send Touch
      midiData[1] = value;

      HandleMidiOut(midiData, numElements);
      break;
    }
    case HV_HASH_BENDOUT:
    {
      uint16_t value = hv_msg_getFloat(m, 0);
      uint8_t lsb  = value & 0x7F;
      uint8_t msb  = (value >> 7) & 0x7F;
      uint8_t ch = hv_msg_getFloat(m, 1);
      ch %= 16;

      const uint8_t numElements = 3;
      uint8_t midiData[numElements];
      midiData[0] = 0xE0 | ch; // send Bend
      midiData[1] = lsb;
      midiData[2] = msb;

      HandleMidiOut(midiData, numElements);
      break;
    }
    // not functional yet
    // case HV_HASH_MIDIOUT: // __hv_midiout
    // {
    //   if (midiOutCount == 0 ) {
    //     uint8_t midiOutData[3];
    //   }

    //   midiOutData[midiOutCount] = hv_msg_getFloat(m, 0);

    //   if (midiOutCount < 2) {
    //     midiOutCount++;
    //     break;
    //   }

    //   HandleMidiOut(midiOutData, 3);
    //   midiOutCount = 0;
    //   break;
    // }
    default:
      break;
  }
}
