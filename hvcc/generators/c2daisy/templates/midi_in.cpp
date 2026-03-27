// Typical Switch case for Message Type.
void HandleMidiMessage(MidiEvent m)
{
  ScopedIrqBlocker block; //< Disables interrupts while in scope

  for (int i = 0; i <= 2; ++i) {
    hv->sendMessageToReceiverV(HV_HASH_MIDIIN, 0, "ff",
    (float) m.data[i],
    (float) m.channel);
  }

  switch(m.type)
  {
    case SystemRealTime: {
      float srtType;

      switch(m.srt_type)
      {
        case TimingClock:
          srtType = MIDI_RT_CLOCK;
          break;
        case Start:
          srtType = MIDI_RT_START;
          break;
        case Continue:
          srtType = MIDI_RT_CONTINUE;
          break;
        case Stop:
          srtType = MIDI_RT_STOP;
          break;
        case ActiveSensing:
          srtType = MIDI_RT_ACTIVESENSE;
          break;
        case Reset:
          srtType = MIDI_RT_RESET;
          break;
      }

      hv->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0, "ff",
        (float) srtType);
      break;
    }
    case NoteOff: {
      NoteOnEvent p = m.AsNoteOn();
      hv->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
        (float) p.note, // pitch
        (float) 0, // velocity
        (float) p.channel);
      break;
    }
    case NoteOn: {
      NoteOnEvent p = m.AsNoteOn();
      hv->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
        (float) p.note, // pitch
        (float) p.velocity, // velocity
        (float) p.channel);
      break;
    }
    case PolyphonicKeyPressure: { // polyphonic aftertouch
      PolyphonicKeyPressureEvent p = m.AsPolyphonicKeyPressure();
      hv->sendMessageToReceiverV(HV_HASH_POLYTOUCHIN, 0, "fff",
        (float) p.pressure, // pressure
        (float) p.note, // note
        (float) p.channel);
      break;
    }
    case ControlChange: {
      ControlChangeEvent p = m.AsControlChange();
      hv->sendMessageToReceiverV(HV_HASH_CTLIN, 0, "fff",
        (float) p.value, // value
        (float) p.control_number, // cc number
        (float) p.channel);
      break;
    }
    case ProgramChange: {
      ProgramChangeEvent p = m.AsProgramChange();
      hv->sendMessageToReceiverV(HV_HASH_PGMIN, 0, "ff",
        (float) p.program,
        (float) p.channel);
      break;
    }
    case ChannelPressure: {
      ChannelPressureEvent p = m.AsChannelPressure();
      hv->sendMessageToReceiverV(HV_HASH_TOUCHIN, 0, "ff",
        (float) p.pressure,
        (float) p.channel);
      break;
    }
    case PitchBend: {
      PitchBendEvent p = m.AsPitchBend();
      // combine 7bit lsb and msb into 32bit int
      hv_uint32_t value = (((hv_uint32_t) m.data[1]) << 7) | ((hv_uint32_t) m.data[0]);
      hv->sendMessageToReceiverV(HV_HASH_BENDIN, 0, "ff",
        (float) value,
        (float) p.channel);
      break;
    }

    default: break;
  }
}
