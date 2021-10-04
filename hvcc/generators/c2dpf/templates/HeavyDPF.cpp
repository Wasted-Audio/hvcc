{{copyright}}

#include "{{class_name}}.hpp"


#define HV_LV2_NUM_PARAMETERS {{receivers|length}}

START_NAMESPACE_DISTRHO


{{class_name}}::{{class_name}}()
 : Plugin(HV_LV2_NUM_PARAMETERS, 0, 0)
{
    {% for k, v in receivers %}
    _parameters[{{loop.index-1}}] = {{v.attributes.default}}f;
    {% endfor %}

    _context = new Heavy_{{name}}(getSampleRate(), {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
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

void {{class_name}}::run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount)
{
  uint32_t framesDone = 0;
  uint32_t curEventIndex = 0;

  _context->process((float**)inputs, outputs, frames);

  while (framesDone < frames)
  {
    while (curEventIndex < midiEventCount && framesDone == midiEvents[curEventIndex].frame)
    {
      if (midiEvents[curEventIndex].size > MidiEvent::kDataSize)
          continue;

      int status = midiEvents[curEventIndex].data[0];
      int command = status & 0xF0;
      int channel = status & 0x0F;
      int data1   = midiEvents[curEventIndex].data[1];
      int data2   = midiEvents[curEventIndex].data[2];

      switch (command) {
        case 0x80:   // note off
        case 0x90: { // note on
          _context->sendMessageToReceiverV(0x67E37CA3, // __hv_notein
              1000.0*frames/getSampleRate(), "fff",
              (float) data1, // pitch
              (float) data2, // velocity
              (float) channel);
          break;
        }
        case 0xB0: { // control change
          _context->sendMessageToReceiverV(0x41BE0F9C, // __hv_ctlin
              1000.0*frames/getSampleRate(), "fff",
              (float) data2, // value
              (float) data1, // controller number
              (float) channel);
          break;
        }
        case 0xC0: { // program change
          _context->sendMessageToReceiverV(0x2E1EA03D, // __hv_pgmin,
              1000.0*frames/getSampleRate(), "ff",
              (float) data1,
              (float) channel);
          break;
        }
        case 0xD0: { // aftertouch
          _context->sendMessageToReceiverV(0x553925BD, // __hv_touchin
              1000.0*frames/getSampleRate(), "ff",
              (float) data1,
              (float) channel);
          break;
        }
        case 0xE0: { // pitch bend
          hv_uint32_t value = (((hv_uint32_t) data2) << 7) | ((hv_uint32_t) data1);
          _context->sendMessageToReceiverV(0x3083F0F7, // __hv_bendin
              1000.0*frames/getSampleRate(), "ff",
              (float) value,
              (float) channel);
          break;
        }
        default: break;
      }
      curEventIndex++;
    }
    framesDone++;
  }
}

// -------------------------------------------------------------------
// Callbacks

void {{class_name}}::sampleRateChanged(double newSampleRate)
{
  delete _context;
  _context = new Heavy_{{name}}(newSampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});

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
