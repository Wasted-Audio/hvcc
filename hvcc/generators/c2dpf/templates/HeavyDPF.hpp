{{copyright}}

#ifndef _HEAVY_LV2_{{name|upper}}_
#define _HEAVY_LV2_{{name|upper}}_

#include "DistrhoPlugin.hpp"
#include "DistrhoPluginInfo.h"
#include "Heavy_{{name}}.hpp"

START_NAMESPACE_DISTRHO

#define HV_DPF_NUM_PARAMETER {{receivers|length + events|length + senders|length + out_events|length}}

static void hvSendHookFunc(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m);
static void hvPrintHookFunc(HeavyContextInterface *c, const char *printLabel, const char *msgString, const HvMessage *m);

class {{class_name}} : public Plugin
{
public:
  enum Parameters
  {
    {%- for k, v in receivers + events + senders + out_events %}
      param{{v.display}},
    {%- endfor %}
  };

{% if meta.port_groups != None %}
  enum PortGroups
  {
{%- if meta.port_groups.input|length or meta.port_groups.output|length or meta.port_groups.params|length %}
  {%- for group, value in (meta.port_groups.input.items()|list) + (meta.port_groups.output.items()|list) + (meta.port_groups.params.items()|list) %}
    kPortGroup{{group|slugify}},
  {%- endfor %}
{%- endif %}
    kPortGroupCount
  };
{%- endif %}

  {{class_name}}();
  ~{{class_name}}() override;

  void handleMidiInput(uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount);
  void handleMidiSend(uint32_t sendHash, const HvMessage *m);
  void hostTransportEvents(uint32_t frames);
  void setOutputEvent(uint32_t id);
  void setOutputParameter(uint32_t sendHash, const HvMessage *m);

protected:
  // -------------------------------------------------------------------
  // Information

  const char* getLabel() const noexcept override
  {
    return "{{name}}";
  }

{%- if meta.description != None %}
  const char* getDescription() const override
  {
    return "{{meta.description}}";
  }
{%- endif %}

  const char* getMaker() const noexcept override
  {
{%- if meta.maker != None %}
    return "{{meta.maker}}";
{% else %}
    return "Wasted Audio";
{%- endif %}
  }

{%- if meta.homepage != None %}
  const char* getHomePage() const override
  {
    return "{{meta.homepage}}";
  }
{%- endif %}

  const char* getLicense() const noexcept override
  {
{%- if meta.license != None %}
    return "{{meta.license}}";
{% else %}
    return "GPL v3+";
{%- endif %}
  }

  uint32_t getVersion() const noexcept override
  {
{%- if meta.version != None %}
    return d_version({{meta.version}});
{% else %}
    return d_version(0, 0, 1);
{%- endif %}
  }

  int64_t getUniqueId() const noexcept override
  {
    return int64_t( {{class_name|uniqueid}} );
  }

  // -------------------------------------------------------------------
  // Init

  void initParameter(uint32_t index, Parameter& parameter) override;
  {% if meta.port_groups != None %}
  void initAudioPort(bool input, uint32_t index, AudioPort& port) override;
  void initPortGroup(uint32_t groupId, PortGroup& portGroup) override;
  {%- endif %}

  // -------------------------------------------------------------------
  // Internal data

  float getParameterValue(uint32_t index) const override;
  void  setParameterValue(uint32_t index, float value) override;

  // -------------------------------------------------------------------
  // Process

  // void activate() override;
  // void deactivate() override;

#if DISTRHO_PLUGIN_WANT_MIDI_INPUT
  void run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount) override;
#else
  void run(const float** inputs, float** outputs, uint32_t frames) override;
#endif

  // -------------------------------------------------------------------
  // Callbacks

  void sampleRateChanged(double newSampleRate) override;

  // -------------------------------------------------------------------

private:
{%- if (receivers|length > 0) or (senders|length > 0) or (events|length > 0) or (out_events|length > 0) %}
  // parameters
  float _parameters[HV_DPF_NUM_PARAMETER];
{%- endif %}

{%- if out_events|length > 0 %}
  struct OutputEvent {
    uint32_t id = 0;
    uint32_t holdSamples = 0;
  };

  OutputEvent outputEvents[{{receivers|length + events|length + senders|length + out_events|length}}];
{%- endif %}

  // transport values
  bool wasPlaying = false;
  double nextClockTick = 0.0;
  double sampleAtCycleStart = 0.0;

  // midi out buffer
  int midiOutCount;
  MidiEvent midiOutEvent;

  // heavy context
  HeavyContextInterface *_context;

  // {{class_name}}<float> f{{name}};

  DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR({{class_name}})
};

// -----------------------------------------------------------------------

END_NAMESPACE_DISTRHO

#endif // _HEAVY_LV2_{{name|upper}}_
{# newline #}
