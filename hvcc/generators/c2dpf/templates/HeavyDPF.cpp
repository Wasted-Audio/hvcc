{{copyright}}

#include "Heavy_{{name}}.h"
#include "{{class_name}}.hpp"
#include <set>


#define HV_LV2_NUM_PARAMETERS {{receivers|length}}

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

#define HV_HASH_DPF_BPM         0xDF8C2721

// midi realtime messages
std::set<int> mrtSet {
  MIDI_RT_CLOCK,
  MIDI_RT_START,
  MIDI_RT_CONTINUE,
  MIDI_RT_STOP,
  MIDI_RT_RESET
};


START_NAMESPACE_DISTRHO


// -------------------------------------------------------------------
// Heavy Send and Print hooks

static void hvSendHookFunc(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m)
{
  {{class_name}}* plugin = ({{class_name}}*)c->getUserData();
  if (plugin != nullptr)
  {
{%- if meta.midi_output is defined and meta.midi_output == 1 %}
#if DISTRHO_PLUGIN_WANT_MIDI_OUTPUT
    plugin->handleMidiSend(sendHash, m);
#endif
{% endif %}
  }
}

static void hvPrintHookFunc(HeavyContextInterface *c, const char *printLabel, const char *msgString, const HvMessage *m)
{
  char buf[64];
  char* dst = buf;
  int len = strnlen(printLabel, 48);
  dst = strncpy(dst, printLabel, len);
  dst = strcpy(dst, " ");
  dst = strncpy(dst, msgString, 63-len);
  printf("> %s \n", buf);
}

// -------------------------------------------------------------------
// Main DPF plugin class

{{class_name}}::{{class_name}}()
 : Plugin(HV_LV2_NUM_PARAMETERS, 0, 0)
{
  {% for k, v in receivers -%}
  _parameters[{{loop.index-1}}] = {{v.attributes.default}}f;
  {% endfor %}

  _context = hv_{{name}}_new_with_options(getSampleRate(), {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  _context->setUserData(this);
  _context->setSendHook(&hvSendHookFunc);
  _context->setPrintHook(&hvPrintHookFunc);

  {% if receivers|length > 0 %}
  // ensure that the new context has the current parameters
  for (int i = 0; i < HV_LV2_NUM_PARAMETERS; ++i) {
    setParameterValue(i, _parameters[i]);
  }
  {%- endif %}
}

{{class_name}}::~{{class_name}}() {
  hv_{{name}}_free(_context);
}

{%- if meta.port_groups is defined %}
{% include 'HeavyDPF_PortGroups.cpp' %}
{%- endif %}

void {{class_name}}::initParameter(uint32_t index, Parameter& parameter)
{
  {%- if receivers|length > 0 -%}
  // initialise parameters with defaults
  switch (index)
  {
    {% for k, v in receivers -%}
      case param{{v.display}}:
        parameter.name = "{{v.display.replace('_', ' ')}}";
        parameter.symbol = "{{v.display|lower}}";
      {%- if v.attributes.type == 'db': %}
        parameter.unit = "dB";
      {%- elif v.attributes.type in ['hz', 'log_hz']: %}
        parameter.unit = "Hz";
      {%- endif %}
        parameter.hints = kParameterIsAutomatable
      {%- if v.attributes.type == 'bool': %}
        | kParameterIsBoolean
      {%- elif v.attributes.type == 'trig': -%}
        | kParameterIsTrigger
      {%- elif v.attributes.type == 'int': -%}
        | kParameterIsInteger
      {%- elif v.attributes.type in ['log', 'log_hz']: -%}
        | kParameterIsLogarithmic
      {%- endif %};
        parameter.ranges.min = {{v.attributes.min}}f;
        parameter.ranges.max = {{v.attributes.max}}f;
        parameter.ranges.def = {{v.attributes.default}}f;
      {%- if v.attributes.type == 'db' and not (meta.enumerators is defined and meta.enumerators[v.display] is defined): %}
        {
          ParameterEnumerationValue* const enumValues = new ParameterEnumerationValue[1];
          enumValues[0].value = {{v.attributes.min}}f;
          enumValues[0].label = "-inf";
          parameter.enumValues.count = 1;
          parameter.enumValues.values = enumValues;
        }
      {%- endif %}
      {%- if meta.enumerators is defined and meta.enumerators[v.display] is defined %}
        {% set enums = meta.enumerators[v.display] %}
        {% set enumlen = enums|length %}
        if (ParameterEnumerationValue *values = new ParameterEnumerationValue[{{enumlen}}])
        {
          parameter.enumValues.restrictedMode = true;
          {% for i in enums -%}
          values[{{loop.index - 1}}].value = {{loop.index - 1}}.0f;
          values[{{loop.index - 1}}].label = "{{i}}";
          {% endfor -%}
          parameter.enumValues.count = {{enumlen}};
          parameter.enumValues.values = values;
        }
      {%- endif %}
        break;
    {% endfor %}
  }
  {% endif %}
}

// -------------------------------------------------------------------
// Internal data

float {{class_name}}::getParameterValue(uint32_t index) const
{
  {%- if receivers|length > 0 %}
  return _parameters[index];
  {% else %}
  return 0.0f;
  {%- endif %}
}

void {{class_name}}::setParameterValue(uint32_t index, float value)
{
  {%- if receivers|length > 0 %}
  switch (index) {
    {% for k, v  in receivers -%}
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
  {%- endif %}
}


// -------------------------------------------------------------------
// Process

// void {{class_name}}::activate()
// {

// }

// void {{class_name}}::deactivate()
// {

// }

{%- if meta.midi_input is defined and meta.midi_input == 1 %}
#if DISTRHO_PLUGIN_WANT_MIDI_INPUT
{% include 'HeavyDPF_MIDI_Input.cpp' %}
#endif
{% endif %}

{%- if meta.midi_output is defined and meta.midi_output == 1 %}
#if DISTRHO_PLUGIN_WANT_MIDI_OUTPUT
{% include 'HeavyDPF_MIDI_Output.cpp' %}
#endif
{% endif %}



// -------------------------------------------------------------------
// DPF Plugin run() loop

#if DISTRHO_PLUGIN_WANT_MIDI_INPUT
void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  handleMidiInput(frames, midiEvents, midiEventCount);
#else
void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames)
{
#endif
  const TimePosition& timePos(getTimePosition());
  if (timePos.playing && timePos.bbt.valid)
    _context->sendMessageToReceiverV(HV_HASH_DPF_BPM, 0, "f", timePos.bbt.beatsPerMinute);

  _context->process((float**)inputs, outputs, frames);
}

// -------------------------------------------------------------------
// Callbacks

void {{class_name}}::sampleRateChanged(double newSampleRate)
{
  hv_{{name}}_free(_context);

  _context = hv_{{name}}_new_with_options(getSampleRate(), {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  _context->setUserData(this);
  _context->setSendHook(&hvSendHookFunc);
  _context->setPrintHook(&hvPrintHookFunc);

  {% if receivers|length > 0 -%}
  // ensure that the new context has the current parameters
  for (int i = 0; i < HV_LV2_NUM_PARAMETERS; ++i) {
    setParameterValue(i, _parameters[i]);
  }
  {%- endif %}
}


// -----------------------------------------------------------------------
/* Plugin entry point, called by DPF to create a new plugin instance. */

Plugin* createPlugin()
{
    return new {{class_name}}();
}

// -----------------------------------------------------------------------

END_NAMESPACE_DISTRHO
