{{copyright}}

#ifndef _HEAVY_LV2_{{name|upper}}_
#define _HEAVY_LV2_{{name|upper}}_

#include "DistrhoPlugin.hpp"
#include "Heavy_{{name}}.hpp"

START_NAMESPACE_DISTRHO

class {{class_name}} : public Plugin
{
public:
  enum Parameters
  {
    {%- for k, v in receivers %}
      param{{v.display}},
    {%- endfor %}
  };

  {{class_name}}();
  ~{{class_name}}() override;

protected:
  // -------------------------------------------------------------------
  // Information

  const char* getLabel() const noexcept override
  {
    return "{{name}}";
  }

  const char* getDescription() const override
  {
    return "{{description}}";
  }

  const char* getMaker() const noexcept override
  {
    return "Wasted Audio";
}

  const char* getHomePage() const override
  {
    return "https://github.com/wasted.audio/{{name}}";
  }

  const char* getLicense() const noexcept override
  {
    return "GPL v3+";
  }

  uint32_t getVersion() const noexcept override
  {
    return d_version(0, 0, 1);
  }

  int64_t getUniqueId() const noexcept override
  {
    // return d_cconst('W', 'S', 't', 'd');
    return int64_t( {{class_name|uniqueid}} );
  }

  // -------------------------------------------------------------------
  // Init

  void initParameter(uint32_t index, Parameter& parameter) override;

  // -------------------------------------------------------------------
  // Internal data

  float getParameterValue(uint32_t index) const override;
  void  setParameterValue(uint32_t index, float value) override;

  // -------------------------------------------------------------------
  // Process

  // void activate() override;
  // void deactivate() override;
  void run(const float** inputs, float** outputs, uint32_t frames, const MidiEvent* midiEvents, uint32_t midiEventCount) override;

  // -------------------------------------------------------------------
  // Callbacks

  void sampleRateChanged(double newSampleRate) override;

  // -------------------------------------------------------------------

private:
  {%- if receivers|length > 0 %}
  // parameters
  float _parameters[{{receivers|length}}]; // in range of [0,1]
  {%- endif %}

  // heavy context
  HeavyContextInterface *_context;

  // {{class_name}}<float> f{{name}};

  DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR({{class_name}})
};

// -----------------------------------------------------------------------

END_NAMESPACE_DISTRHO

#endif // _HEAVY_LV2_{{name|upper}}_
{# newline #}
