{{copyright}}

#include "HeavyMetaModule_{{name}}.hpp"

#define MM_INPUT_PATCHED        0x1B705A3F  // __mm_in_patched
#define MM_OUTPUT_PATCHED       0xB390A0FB  // __mm_out_patched
#define MM_INPUTS_UNPATCHED     0xAF350DDA  // __mm_in_patched_all
#define MM_OUTPUTS_UNPATCHED    0x2D7EA032  // __mm_out_patched_all


float {{name}}MM::_leds[NUM_LEDS > 0 ? NUM_LEDS : 1] = {0.0f};

void {{name}}MM::hvSendHook(HeavyContextInterface *c, const char *sendName, uint32_t sendHash, const HvMessage *m) {
    {%- if senders|length > 0 %}
    switch (sendHash) {
        {% for k, v in senders -%}
        case {{v.hash}}: // {{v.display}}
            _leds[Led_{{v.display|capitalize}}ID] = (hv_msg_getFloat(m, 0) - {{v.attributes.min}}f) / ({{v.attributes.max}}f - {{v.attributes.min}}f);
            break;
        {% endfor %}
        default:
            break;
    }
    {%- endif %}
}

{{name}}MM::{{name}}MM(double samplerate) {
    hv_context = std::make_unique<Heavy_{{name}}>(samplerate);
    hv_context->setSendHook(&hvSendHook);

    {%- for k,v in receivers %}
    _params[Param_{{v.display|capitalize}}ID] = ({{v.attributes.default}}f - {{v.attributes.min}}f) / ({{v.attributes.max}}f - {{v.attributes.min}}f);
    set_param(Param_{{v.display|capitalize}}ID, _params[Param_{{v.display|capitalize}}ID]);
    {%- endfor %}
}

void {{name}}MM::update() {
    if (!hv_context) return;

    static constexpr float kInputScale  = 0.1f;
    static constexpr float kOutputScale = 10.0f;

    float scaled_in[NUM_INPUTS > 0 ? NUM_INPUTS : 1];
    for (int i = 0; i < NUM_INPUTS; ++i)
        scaled_in[i] = input_buffers[i] * kInputScale;

    float* in_ptr  = (NUM_INPUTS  > 0) ? scaled_in       : nullptr;
    float* out_ptr = (NUM_OUTPUTS > 0) ? output_buffers  : nullptr;

    hv_context->processInline(in_ptr, out_ptr, 1);

    for (int i = 0; i < NUM_OUTPUTS; ++i)
        current_outputs[i] = output_buffers[i] * kOutputScale;
}

void {{name}}MM::set_samplerate(float sr) {
    hv_context = std::make_unique<Heavy_{{name}}>(static_cast<double>(sr));
    hv_context->setSendHook(&hvSendHook);

    {%- for k,v in receivers %}
    set_param(Param_{{v.display|capitalize}}ID, _params[Param_{{v.display|capitalize}}ID]);
    {%- endfor %}
}

void {{name}}MM::set_param(int param_id, float val) {
    if (param_id < 0 || param_id >= NUM_PARAMS) {
        return;
    }

    _params[param_id] = val;

    switch (param_id) {
        {%- for k,v in receivers %}
        case Param_{{v.display|capitalize}}ID:
            hv_context->sendFloatToReceiver(Heavy_{{name}}::Parameter::In::{{k|upper}}, val * ({{v.attributes.max}}f - {{v.attributes.min}}f) + {{v.attributes.min}}f);
            break;
        {%- endfor %}
        default:
            break;
    }
}

float {{name}}MM::get_param(int param_id) const {
    if (param_id < 0 || param_id >= NUM_PARAMS) {
        return 0.0f;
    }

    return _params[param_id];
}

void {{name}}MM::set_input(int input_id, float val) {
    if (input_id < 0 || input_id >= NUM_INPUTS) {
        return;
    }

    input_buffers[input_id] = val;
}

float {{name}}MM::get_output(int output_id) const {
    if (output_id < 0 || output_id >= NUM_OUTPUTS) {
        return 0.0f;
    }

    return current_outputs[output_id];
}

float {{name}}MM::get_led_brightness(int led_id) const {
    if (led_id < 0 || led_id >= NUM_LEDS) {
        return 0.0f;
    }

    switch (led_id) {
        {%- for k,v in senders %}
        case Led_{{v.display|capitalize}}ID:
            return _leds[Led_{{v.display|capitalize}}ID];
        {%- endfor %}
        default:
            return 0.0f;
    }
}


// Jack input and output detections

void {{name}}MM::mark_input_unpatched(int input_id) {
    if (input_id < 0 || input_id >= NUM_INPUTS) {
        return;
    }

    hv_context->sendMessageToReceiverV(MM_INPUT_PATCHED, 0, "ff",
        (float) input_id, 0.0f
    );
}

void {{name}}MM::mark_input_patched(int input_id) {
    if (input_id < 0 || input_id >= NUM_INPUTS) {
        return;
    }

    hv_context->sendMessageToReceiverV(MM_INPUT_PATCHED, 0, "ff",
        (float) input_id, 1.0f
    );
}

void {{name}}MM::mark_output_unpatched(int output_id) {
    if (output_id < 0 || output_id >= NUM_OUTPUTS) {
        return;
    }

    hv_context->sendMessageToReceiverV(MM_OUTPUT_PATCHED, 0, "ff",
        (float) output_id, 0.0f
    );
}

void {{name}}MM::mark_output_patched(int output_id) {
    if (output_id < 0 || output_id >= NUM_OUTPUTS) {
        return;
    }

    hv_context->sendMessageToReceiverV(MM_OUTPUT_PATCHED, 0, "ff",
        (float) output_id, 1.0f
    );
}

void {{name}}MM::mark_all_inputs_unpatched() {
    hv_context->sendBangToReceiver(MM_INPUTS_UNPATCHED);
}

void {{name}}MM::mark_all_outputs_unpatched() {
    hv_context->sendBangToReceiver(MM_OUTPUTS_UNPATCHED);
}
