{{copyright}}

#include "{{class_name}}.hpp"


#define HV_LV2_NUM_PARAMETERS {{receivers|length}}

#define HV_HASH_NOTEIN    0x67e37ca3
#define HV_HASH_CTLIN     0x41be0f9c
#define HV_HASH_BENDIN    0x3083f0f7
#define HV_HASH_TOUCHIN   0x553925bd
#define HV_HASH_PGMIN     0x2e1ea03d

#define HV_HASH_NOTEOUT   0xd1d4ac2
#define HV_HASH_CTLOUT    0xe5e2a040
#define HV_HASH_BENDOUT   0xe8458013
#define HV_HASH_TOUCHOUT  0x476d4387
#define HV_HASH_PGMOUT    0x8753e39e

START_NAMESPACE_DISTRHO

static void sendHookFunc(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m)
{
  printf("> midi output stuff! \n");
  {{class_name}}* plugin = ({{class_name}}*)c->getUserData();
  if (plugin != nullptr)
  {
    plugin->handleMidiSend(sendHash, m);
  }
}

  static void hvPrintHook(HeavyContextInterface* ctxt, const char *printLabel, const char *msgString, const HvMessage *m)
  {
    char buf[64];
    char* dst = buf;
    int len = strnlen(printLabel, 48);
    dst = stpncpy(dst, printLabel, len);
    dst = stpcpy(dst, " ");
    dst = stpncpy(dst, msgString, 63-len);
    printf("> %s \n", buf);
  }


{{class_name}}::{{class_name}}()
 : Plugin(HV_LV2_NUM_PARAMETERS, 0, 0)
{
    {% for k, v in receivers %}
    _parameters[{{loop.index-1}}] = {{v.attributes.default}}f;
    {% endfor %}

    _context = new Heavy_{{name}}(getSampleRate(), {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
    _context->setUserData(this);
    _context->setSendHook(&sendHookFunc);
    _context->setPrintHook(&hvPrintHook);

    {% if receivers|length > 0 %}
    // ensure that the new context has the current parameters
    for (int i = 0; i < HV_LV2_NUM_PARAMETERS; ++i) {
      setParameterValue(i, _parameters[i]);
    }
    {% endif %}
}

{{class_name}}::~{{class_name}}() {
  delete _context;
}

void {{class_name}}::initParameter(uint32_t index, Parameter& parameter)
{
  {% if receivers|length > 0 %}
  // initialise parameters with defaults
  switch (index)
  {
    {% for k, v in receivers %}
      case param{{v.display}}:
        parameter.name = "{{v.display.replace('_', ' ')}}";
        parameter.symbol = "{{v.display|lower}}";
        parameter.hints = kParameterIsAutomable
      {% if v.attributes.type == 'bool': %}
        | kParameterIsBoolean
      {% elif v.attributes.type == 'trig': %}
        | kParameterIsTrigger
      {% endif %};
        parameter.ranges.min = {{v.attributes.min}}f;
        parameter.ranges.max = {{v.attributes.max}}f;
        parameter.ranges.def = {{v.attributes.default}}f;
        break;
    {% endfor %}
  }
  {% endif %}
}

// -------------------------------------------------------------------
// Internal data

float {{class_name}}::getParameterValue(uint32_t index) const
{
  {% if receivers|length > 0 %}
  return _parameters[index];
  {% else %}
  return 0.0f;
  {% endif %}
}

void {{class_name}}::setParameterValue(uint32_t index, float value)
{
  {% if receivers|length > 0 %}
  switch (index) {
    {% for k, v  in receivers %}
    case {{loop.index-1}}: {
      _context->sendFloatToReceiver(
          Heavy_{{name}}::Parameter::In::{{k|upper}},
          value);
      break;
    }
    {% endfor %}
    default: return;
  }
  _parameters[index] = value;
  {% else %}
  // nothing to do
  {% endif %}
}


// -------------------------------------------------------------------
// Process

// void {{class_name}}::activate()
// {

// }

// void {{class_name}}::deactivate()
// {

// }

void {{class_name}}::handleMidiInput(uint32_t curEventIndex, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  int status = midiEvents[curEventIndex].data[0];
  int command = status & 0xF0;
  int channel = status & 0x0F;
  int data1   = midiEvents[curEventIndex].data[1];
  int data2   = midiEvents[curEventIndex].data[2];

  switch (command) {
    case 0x80:   // note off
    case 0x90: { // note on
      printf("> midi input stuff! \n");
      printf("> note: %d - velocity: %d - ch: %d \n", data1, data2, channel);
      _context->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
        (float) data1, // pitch
        (float) data2, // velocity
        (float) channel);
      break;
    }
    case 0xB0: { // control change
      _context->sendMessageToReceiverV(HV_HASH_CTLIN, 0, "fff",
        (float) data2, // value
        (float) data1, // controller number
        (float) channel);
      break;
    }
    case 0xC0: { // program change
      _context->sendMessageToReceiverV(HV_HASH_PGMIN, 0, "ff",
        (float) data1,
        (float) channel);
      break;
    }
    case 0xD0: { // aftertouch
      _context->sendMessageToReceiverV(HV_HASH_TOUCHIN, 0, "ff",
        (float) data1,
        (float) channel);
      break;
    }
    case 0xE0: { // pitch bend
      hv_uint32_t value = (((hv_uint32_t) data2) << 7) | ((hv_uint32_t) data1);
      _context->sendMessageToReceiverV(HV_HASH_BENDIN, 0, "ff",
        (float) value,
        (float) channel);
      break;
    }
    default: break;
  }
}

void {{class_name}}::handleMidiSend(uint32_t sendHash, const HvMessage *m)
{
    switch(sendHash){
      case HV_HASH_NOTEOUT: // __hv_noteout
      {
        uint8_t note = hv_msg_getFloat(m, 0);
        uint8_t velocity = hv_msg_getFloat(m, 1);
        uint8_t ch = hv_msg_getFloat(m, 2);
        printf("> note: %d - velocity: %d - ch: %d \n", note, velocity, ch);

        MidiEvent midiSendEvent;
        midiSendEvent.frame = 0;
        midiSendEvent.size = m->numElements;
        midiSendEvent.dataExt = nullptr;

        if (velocity == 127){
          midiSendEvent.data[0] = 0x80 | ch; // noteoff
        } else {
          midiSendEvent.data[0] = 0x90 | ch; // noteon
        }
        midiSendEvent.data[1] = note;
        midiSendEvent.data[2] = velocity;
        midiSendEvent.data[3] = 0;

        writeMidiEvent(midiSendEvent);
        break;
      }
      case HV_HASH_CTLOUT:
      {
        uint8_t value = hv_msg_getFloat(m, 0);
        uint8_t cc = hv_msg_getFloat(m, 1);
        uint8_t ch = hv_msg_getFloat(m, 2);
        printf("> value: %d - cc: %d - ch: %d \n", value, cc, ch);

        MidiEvent midiSendEvent;
        midiSendEvent.frame = 0;
        midiSendEvent.size = m->numElements;
        midiSendEvent.dataExt = nullptr;

        midiSendEvent.data[0] = 0xB0 | ch; // send CC
        midiSendEvent.data[1] = cc;
        midiSendEvent.data[2] = value;
        midiSendEvent.data[3] = 0;

        writeMidiEvent(midiSendEvent);
        break;
      }
      case HV_HASH_PGMOUT:
      {
        uint8_t cc_val = hv_msg_getFloat(m, 0);
        uint8_t cc_num = hv_msg_getFloat(m, 1);
        uint8_t ch = hv_msg_getFloat(m, 2);
        printf("> cc_val: %d - cc_num: %d - ch: %d \n", cc_val, cc_num, ch);

        MidiEvent midiSendEvent;
        midiSendEvent.frame = 0;
        midiSendEvent.size = m->numElements;
        midiSendEvent.dataExt = nullptr;

        midiSendEvent.data[0] = 0xC0 | ch; // send Program Change
        midiSendEvent.data[1] = cc_num;
        midiSendEvent.data[2] = cc_val;
        midiSendEvent.data[3] = 0;
        break;
      }
      case HV_HASH_TOUCHOUT:
      {
        uint8_t value = hv_msg_getFloat(m, 0);
        uint8_t ch = hv_msg_getFloat(m, 2);
        printf("> value: %d - ch: %d \n", value, ch);

        MidiEvent midiSendEvent;
        midiSendEvent.frame = 0;
        midiSendEvent.size = m->numElements;
        midiSendEvent.dataExt = nullptr;

        midiSendEvent.data[0] = 0xD0 | ch; // send Touch
        midiSendEvent.data[1] = value;
        midiSendEvent.data[2] = 0;
        midiSendEvent.data[3] = 0;
        break;
      }
      case HV_HASH_BENDOUT:
      {
        break;
      }
      default:
        break;
  }

}

void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  uint32_t framesDone = 0;
  uint32_t curEventIndex = 0;

  // while (framesDone < frames)
  // {
  //   while (curEventIndex < midiEventCount && framesDone == midiEvents[curEventIndex].frame)
  //   {
  //     if (midiEvents[curEventIndex].size > MidiEvent::kDataSize)
  //       continue;

  //     handleMidiInput(curEventIndex, midiEvents, midiEventCount);
  //     curEventIndex++;
  //   }
  //   framesDone++;
  // }

  for (uint32_t i=0; i < midiEventCount; ++i)
  {
    handleMidiInput(i, midiEvents, midiEventCount);
  }

  _context->process((float**)inputs, outputs, frames);
}

// -------------------------------------------------------------------
// Callbacks

void {{class_name}}::sampleRateChanged(double newSampleRate)
{
  delete _context;
  _context = new Heavy_{{name}}(newSampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  _context->setUserData(this);
  _context->setSendHook(&sendHookFunc);

  {% if receivers|length > 0 %}
  // ensure that the new context has the current parameters
  for (int i = 0; i < HV_LV2_NUM_PARAMETERS; ++i) {
    setParameterValue(i, _parameters[i]);
  }
  {% endif %}
}


// -----------------------------------------------------------------------
/* Plugin entry point, called by DPF to create a new plugin instance. */

Plugin* createPlugin()
{
    return new {{class_name}}();
}

// -----------------------------------------------------------------------

END_NAMESPACE_DISTRHO
