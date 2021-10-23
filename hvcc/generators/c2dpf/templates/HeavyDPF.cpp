{{copyright}}

#include "{{class_name}}.hpp"


#define HV_LV2_NUM_PARAMETERS {{receivers|length}}

#define HV_HASH_NOTEIN    0x67e37ca3
#define HV_HASH_CTLIN     0x41be0f9c
#define HV_HASH_PGMIN     0x2e1ea03d
#define HV_HASH_TOUCHIN   0x553925bd
#define HV_HASH_BENDIN    0x3083f0f7

#define HV_HASH_NOTEOUT   0xd1d4ac2
#define HV_HASH_CTLOUT    0xe5e2a040
#define HV_HASH_PGMOUT    0x8753e39e
#define HV_HASH_TOUCHOUT  0x476d4387
#define HV_HASH_BENDOUT   0xe8458013

START_NAMESPACE_DISTRHO

static void hvSendHookFunc(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m)
{
  {{class_name}}* plugin = ({{class_name}}*)c->getUserData();
  if (plugin != nullptr)
  {
#if DISTRHO_PLUGIN_WANT_MIDI_OUTPUT
    plugin->handleMidiSend(sendHash, m);
#endif
  }
}

static void hvPrintHookFunc(HeavyContextInterface *c, const char *printLabel, const char *msgString, const HvMessage *m)
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
  _context->setSendHook(&hvSendHookFunc);
  _context->setPrintHook(&hvPrintHookFunc);

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

#if DISTRHO_PLUGIN_WANT_MIDI_INPUT
void {{class_name}}::handleMidiInput(uint32_t curEventIndex, const MidiEvent* midiEvents)
{
  int status = midiEvents[curEventIndex].data[0];
  int command = status & 0xF0;
  int channel = status & 0x0F;
  int data1   = midiEvents[curEventIndex].data[1];
  int data2   = midiEvents[curEventIndex].data[2];

  switch (command) {
    case 0x80: {  // note off
      _context->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
        (float) data1, // pitch
        (float) 0, // velocity
        (float) channel);
      break;
    }
    case 0x90: { // note on
      _context->sendMessageToReceiverV(HV_HASH_NOTEIN, 0, "fff",
        (float) data1, // pitch
        (float) data2, // velocity
        (float) channel);
      break;
    }
    case 0xB0: { // control change
      _context->sendMessageToReceiverV(HV_HASH_CTLIN, 0, "fff",
        (float) data2, // value
        (float) data1, // cc number
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
      // combine 7bit lsb and msb into 32bit int
      hv_uint32_t value = (((hv_uint32_t) data2) << 7) | ((hv_uint32_t) data1);
      _context->sendMessageToReceiverV(HV_HASH_BENDIN, 0, "ff",
        (float) value,
        (float) channel);
      break;
    }
    default: break;
  }
}
#endif

#if DISTRHO_PLUGIN_WANT_MIDI_OUTPUT
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

      midiSendEvent.size = 3;
      if (velocity > 0){
        midiSendEvent.data[0] = 0x90 | ch; // noteon
      } else {
        midiSendEvent.data[0] = 0x80 | ch; // noteoff
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

      midiSendEvent.size = 3;
      midiSendEvent.data[0] = 0xB0 | ch; // send CC
      midiSendEvent.data[1] = cc;
      midiSendEvent.data[2] = value;
      midiSendEvent.data[3] = 0;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_PGMOUT:
    {
      uint8_t pgm = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);

      midiSendEvent.size = 2;
      midiSendEvent.data[0] = 0xC0 | ch; // send Program Change
      midiSendEvent.data[1] = pgm;
      midiSendEvent.data[2] = 0;
      midiSendEvent.data[3] = 0;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_TOUCHOUT:
    {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);

      midiSendEvent.size = 2;
      midiSendEvent.data[0] = 0xD0 | ch; // send Touch
      midiSendEvent.data[1] = value;
      midiSendEvent.data[2] = 0;
      midiSendEvent.data[3] = 0;

      writeMidiEvent(midiSendEvent);
      break;
    }
    case HV_HASH_BENDOUT:
    {
      uint16_t value = hv_msg_getFloat(m, 0);
      uint8_t lsb  = value & 0x7F;
      uint8_t msb  = (value >> 7) & 0x7F;
      uint8_t ch = hv_msg_getFloat(m, 1);

      midiSendEvent.size = 3;
      midiSendEvent.data[0] = 0xE0 | ch; // send Bend
      midiSendEvent.data[1] = lsb;
      midiSendEvent.data[2] = msb;
      midiSendEvent.data[3] = 0;

      writeMidiEvent(midiSendEvent);
      break;
    }
    default:
      break;
  }
}
#endif

#if DISTRHO_PLUGIN_WANT_MIDI_INPUT
void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  for (uint32_t i=0; i < midiEventCount; ++i)
  {
    handleMidiInput(i, midiEvents);
  }
#else
void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames)
{
#endif

  _context->process((float**)inputs, outputs, frames);
}

// -------------------------------------------------------------------
// Callbacks

void {{class_name}}::sampleRateChanged(double newSampleRate)
{
  delete _context;

  _context = new Heavy_{{name}}(newSampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  _context->setUserData(this);
  _context->setSendHook(&hvSendHookFunc);
  _context->setPrintHook(&hvPrintHookFunc);

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
