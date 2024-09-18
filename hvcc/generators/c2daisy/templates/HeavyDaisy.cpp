{{copyright}}

#include "Heavy_{{patch_name}}.h"
#include "Heavy_{{patch_name}}.hpp"
#include "HeavyDaisy_{{patch_name}}.hpp"

#define SAMPLE_RATE {{samplerate}}.f

{% if has_midi or usb_midi %}
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
{% endif %}

using namespace daisy;

json2daisy::Daisy{{ class_name|capitalize }} hardware;

Heavy_{{patch_name}}* hv;

void audiocallback(daisy::AudioHandle::InputBuffer in, daisy::AudioHandle::OutputBuffer out, size_t size);
static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m);
{% if debug_printing is sameas true %}
static void printHook(HeavyContextInterface *c, const char *printLabel, const char *msgString, const HvMessage *m);
/** FIFO to hold messages as we're ready to print them */
FIFO<FixedCapStr<64>, 64> event_log;
{% elif usb_midi is sameas true %}
daisy::MidiUsbHandler midiusb;
{% endif %}
// int midiOutCount;
// uint8_t* midiOutData;
void CallbackWriteIn(Heavy_{{patch_name}}* hv);
void LoopWriteIn(Heavy_{{patch_name}}* hv);
void CallbackWriteOut();
void LoopWriteOut();
void PostProcess();
void Display();

{% if  output_parameters|length > 0 %}
constexpr int DaisyNumOutputParameters = {{output_parameters|length}};
/** This array holds the output values received from PD hooks. These values are
 *  then written at the appropriate time in the following callback or loop.
 */
float output_data[DaisyNumOutputParameters];

struct DaisyHvParamOut
{
	uint32_t hash;
	uint32_t index;
  void (*hook_write_out)(float);

	void Process(float sig)
	{
		output_data[index] = sig;
    if (hook_write_out)
      (*hook_write_out)(sig);
	}
};

{% for param in hook_write_out %}
void {{param.name}}_hook(float sig) {
  {{param.process}}
};
{% endfor %}

DaisyHvParamOut DaisyOutputParameters[DaisyNumOutputParameters] = {
	{% for param in output_parameters %}
  {% if param.hook %}
    { (uint32_t) HV_{{patch_name|upper}}_PARAM_OUT_{{param.hash_enum|upper}}, {{param.index}}, &{{param.name}}_hook }, // {{param.name}}
  {% else %}
		{ (uint32_t) HV_{{patch_name|upper}}_PARAM_OUT_{{param.hash_enum|upper}}, {{param.index}}, nullptr }, // {{param.name}}
  {% endif %}
	{% endfor %}
};
{% endif %}

{% if (has_midi is sameas true) or (usb_midi is sameas true) %}
// Typical Switch case for Message Type.
void HandleMidiMessage(MidiEvent m)
{
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
{% endif %}

int main(void)
{
  hardware.Init(true);
  hv = new Heavy_{{patch_name}}(SAMPLE_RATE, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});

  {% if samplerate %}
  hardware.SetAudioSampleRate({{samplerate}});
  {% endif %}
  {% if blocksize %}
  hardware.SetAudioBlockSize({{blocksize}});
  {% endif %}
  {% if has_midi is sameas true %}
  MidiUartHandler::Config midi_config;
  hardware.midi.Init(midi_config);
  hardware.midi.StartReceive();
  {% endif %}
  {% if (debug_printing is not sameas true) and (usb_midi is sameas true) %}
  MidiUsbHandler::Config midiusb_config;
  midiusb.Init(midiusb_config);
  midiusb.StartReceive();
  {% endif %}

  hardware.StartAudio(audiocallback);
  {% if debug_printing is sameas true %}
  hardware.som.StartLog();
  hv->setPrintHook(printHook);

  uint32_t now      = System::GetNow();
  uint32_t log_time = System::GetNow();
  {% endif %}
  hv->setSendHook(sendHook);

  for(;;)
  {
    {% if debug_printing %}
    now = System::GetNow();
    {% endif %}

    hardware.LoopProcess();
    {% if has_midi %}
    hardware.midi.Listen();
    while(hardware.midi.HasEvents())
    {
      HandleMidiMessage(hardware.midi.PopEvent());
    }
    {% endif %}
    {% if (debug_printing is not sameas true) and (usb_midi is sameas true) %}
    midiusb.Listen();
    while(midiusb.HasEvents())
    {
      HandleMidiMessage(midiusb.PopEvent());
    }
    {% endif %}
    Display();
    {% if loop_write_in|length > 0 %}
    LoopWriteIn(hv);
    {% endif %}
    {% if  output_parameters|length > 0 %}
    LoopWriteOut();
    {% endif %}

    {% if debug_printing is sameas true %}
    /** Now separately, every 5ms we'll print the top message in our queue if there is one */
    if(now - log_time > 5)
    {
      log_time = now;
      if(!event_log.IsEmpty())
      {
        auto msg = event_log.PopFront();
        hardware.som.PrintLine(msg);
      }
    }
    {% endif %}
  }
}

/** The audio processing function. At the standard 48KHz sample rate and a block
 *  size of 48, this will fire every millisecond.
 */
void audiocallback(daisy::AudioHandle::InputBuffer in, daisy::AudioHandle::OutputBuffer out, size_t size)
{
  {% if num_output_channels == 0 %}
  // A zero fill to keep I/O quiet for a patch lacking ADC~/DAC~
  for (size_t chn = 0; chn < {{max_channels}}; chn++)
  {
    for (size_t i = 0; i < size; i++)
      out[chn][i] = 0;
  }
  {% endif %}
  {% if  parameters|length > 0 %}
  hardware.ProcessAllControls();
  CallbackWriteIn(hv);
  {% endif %}
  hv->process((float**)in, (float**)out, size);
  {% if  output_parameters|length > 0 %}
  CallbackWriteOut();
  {% endif %}
  hardware.PostProcess();
}

{% if (has_midi is sameas true) or (usb_midi is sameas true) %}
void HandleMidiOut(uint8_t *midiData, const uint8_t numElements)
{
  {% if has_midi is sameas true %}
  hardware.midi.SendMessage(midiData, numElements);
  {% endif %}
  {% if (debug_printing is not sameas true) and (usb_midi is sameas true) %}
  midiusb.SendMessage(midiData, numElements);
  {% endif %}
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
{% endif %}


/** Receives messages from PD and writes them to the appropriate
 *  index in the `output_data` array, to be written later.
 */
static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m)
{
  {% if  output_parameters|length > 0 %}
  for (int i = 0; i < DaisyNumOutputParameters; i++)
  {
    if (DaisyOutputParameters[i].hash == receiverHash)
    {
      DaisyOutputParameters[i].Process(msg_getFloat(m, 0));
    }
  }
  {% endif %}
  {% if (has_midi is sameas true) or (usb_midi is sameas true) %}
  HandleMidiSend(receiverHash, m);
  {% endif %}
}

{% if debug_printing is sameas true %}
/** Receives messages from the PD [print] object and writes them to the serial console.
 *
 */
static void printHook(HeavyContextInterface *c, const char *printLabel, const char *msgString, const HvMessage *m)
{
  char buf[64];
  char *dst = buf;
  int len = strnlen(printLabel, 48);
  dst = stpncpy(dst, printLabel, len);
  dst = stpcpy(dst, " ");
  dst = stpncpy(dst, msgString, 63-len);

  /** Regardless of message, let's add the message data to our queue to output */
  event_log.PushBack(buf);
}
{% endif %}

/** Sends signals from the Daisy hardware to the PD patch via the receive objects during the main loop
 *
 */
void LoopWriteIn(Heavy_{{patch_name}}* hv)
{
  {% for param in loop_write_in %}
  {% if param.bool %}
  if ({{param.process}})
    hv->sendBangToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}});
  {% else %}
  hv->sendFloatToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}, {{param.process}});
  {% endif %}
  {% endfor %}
}

/** Sends signals from the Daisy hardware to the PD patch via the receive objects during the audio callback
 *
 */
void CallbackWriteIn(Heavy_{{patch_name}}* hv)
{
  {% for param in callback_write_in %}
  {% if param.bool %}
  if ({{param.process}})
    hv->sendBangToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}});
  {% else %}
  hv->sendFloatToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}, {{param.process}});
  {% endif %}
  {% endfor %}
}

/** Writes the values sent to PD's receive objects to the Daisy hardware during the main loop
 *
 */
void LoopWriteOut() {
  {% for param in loop_write_out %}
  {% if param.bool %}
  if ({{param.value}})
    {{param.process}}
  {% else %}
  {{param.process}}
  {% endif %}
  {% endfor %}
}

/** Writes the values sent to PD's receive objects to the Daisy hardware during the audio callback
 *
 */
void CallbackWriteOut() {
  {% for param in callback_write_out %}
  {% if param.bool %}
  if ({{param.value}})
    {{param.process}}
  {% else %}
  {{param.process}}
  {% endif %}
  {% endfor %}
}

/** Handles the display code if the hardware defines a display
 *
 */
void Display() {
  {{displayprocess}}
}
