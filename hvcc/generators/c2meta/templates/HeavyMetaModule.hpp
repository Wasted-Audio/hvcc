#pragma once

#include "CoreModules/CoreProcessor.hh"
#include <memory>
#include "Heavy_{{name}}.hpp"


constexpr int NUM_PARAMS = {{ receivers|length }};
constexpr int NUM_LEDS = {{ senders|length }};
constexpr int NUM_INPUTS = {{ num_input_channels }};
constexpr int NUM_OUTPUTS = {{ num_output_channels }};

{% if (receivers|length > 0) %}
enum {
    {%- for k,v in receivers %}
    Param_{{v.display|capitalize}}ID,
    {%- endfor %}
};
{% endif %}
{%- if (num_input_channels > 0) %}
enum {
    {%- for n in range(0, num_input_channels) %}
    InputID{{n}},
    {%- endfor %}
};
{% endif %}
{%- if (num_output_channels > 0) %}
enum {
    {%- for n in range(0, num_output_channels) %}
    OutputID{{n}},
    {%- endfor %}
};
{% endif %}
{%- if (senders|length > 0) %}
enum {
    {%- for k,v in senders %}
    Led_{{v.display|capitalize}}ID,
    {%- endfor %}
};
{% endif %}

class {{name}}MM : public CoreProcessor {
public:
    explicit {{name}}MM(double samplerate = 48000.0);
    ~{{name}}MM() override = default;

    static float _leds[NUM_LEDS > 0 ? NUM_LEDS : 1];

    void update() override;
    void set_samplerate(float sr) override;
    void set_param(int param_id, float val) override;
    float get_param(int param_id) const override;
    void set_input(int input_id, float val) override;
    float get_output(int output_id) const override;
    float get_led_brightness(int led_id) const override;

private:
    static void hvSendHook(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m);

    std::unique_ptr<HeavyContextInterface> hv_context;

    float _params[NUM_PARAMS > 0 ? NUM_PARAMS : 1] = {0.0f};
    float input_buffers[NUM_INPUTS > 0 ? NUM_INPUTS : 1] = {0.0f};
    float output_buffers[NUM_OUTPUTS > 0 ? NUM_OUTPUTS : 1] = {0.0f};
    float current_outputs[NUM_OUTPUTS > 0 ? NUM_OUTPUTS : 1] = {0.0f};
};
