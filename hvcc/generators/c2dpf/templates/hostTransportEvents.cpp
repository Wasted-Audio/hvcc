// -------------------------------------------------------------------
// Host Transport Events handler

void {{class_name}}::hostTransportEvents(uint32_t frames)
{
  // Realtime events
  const TimePosition& timePos(getTimePosition());
  bool reset = false;

  if (timePos.playing)
  {
    if (timePos.frame == 0)
    {
      _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0,
        "ff", (float) MIDI_RT_RESET, 0.0);
      reset = true;
    }

    if (! this->wasPlaying)
    {
      if (timePos.frame == 0)
      {
        _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0,
          "ff", (float) MIDI_RT_START, 0.0);
      }
      if (! reset)
      {
        _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0,
          "ff", (float) MIDI_RT_CONTINUE, 0.0);
      }
    }
  }
  else if (this->wasPlaying)
  {
    _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, 0,
      "ff", (float) MIDI_RT_STOP, 0.0);
  }
  this->wasPlaying = timePos.playing;

  // sending clock ticks
  if (timePos.playing && timePos.bbt.valid)
  {
    float samplesPerBeat = 60 * getSampleRate() / timePos.bbt.beatsPerMinute;
    float samplesPerTick = samplesPerBeat / 24.0;

    /* get state */
    double nextClockTick = this->nextClockTick;
    double sampleAtCycleStart = this->sampleAtCycleStart;
    double sampleAtCycleEnd = sampleAtCycleStart + frames;

    if (nextClockTick >= 0 && sampleAtCycleStart >= 0 && sampleAtCycleEnd > sampleAtCycleStart) {
      while (nextClockTick < sampleAtCycleEnd) {
        double delayMs = 1000*(nextClockTick - sampleAtCycleStart)/getSampleRate();
        if (delayMs >= 0.0) {
          _context->sendMessageToReceiverV(HV_HASH_MIDIREALTIMEIN, delayMs,
            "ff", (float) MIDI_RT_CLOCK, 0.0);
        }
        nextClockTick += samplesPerTick;
      }
    }

    /* save variables for next cycle */
    this->sampleAtCycleStart = sampleAtCycleEnd;
    this->nextClockTick = nextClockTick;
  }
}
