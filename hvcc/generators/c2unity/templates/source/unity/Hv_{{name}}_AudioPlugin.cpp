{{copyright}}

// http://docs.unity3d.com/500/Documentation/Manual/AudioMixerNativeAudioPlugin.html

#include "AudioPluginUtil.h"
#include "heavy/Heavy_{{patch_name}}.hpp"

namespace Hv_{{patch_name}}_UnityPlugin {

  enum Param {
    {%- for k, v in parameters %}
    P_{{k|upper}},
    {%- endfor %}
    P_NUM_HV_PARAMS_
  };

  struct EffectData {
    struct Data {
      float p[{{parameters|length if parameters|length > 0 else 1}}];
      HeavyContextInterface *context;
    } data;
  };

  int InternalRegisterEffectDefinition(UnityAudioEffectDefinition& definition) {
    int numparams = P_NUM_HV_PARAMS_;
    definition.paramdefs = new UnityAudioParameterDefinition[numparams];
    // channels will be set to 0 if numInputChannels > 0 else it will be set to numOutputChannels
    definition.channels = {{0 if num_input_channels else num_output_channels}};
    {%- for k, v in parameters %}
    {%- if v.display|length > 15 %}
#if HV_WIN
    // Unity Windows doesn't seem to like parameter names that are longer than 15 chars
    RegisterParameter(definition, "{{v.display|cap(15)}}", "", {{v.attributes.min}}f, {{v.attributes.max}}f, {{v.attributes.default}}f, 1.0f, 1.0f, P_{{k|upper}}, "{{v.display}}");
#else
    RegisterParameter(definition, "{{v.display}}", "", {{v.attributes.min}}f, {{v.attributes.max}}f, {{v.attributes.default}}f, 1.0f, 1.0f, P_{{k|upper}}, "{{v.display}}");
#endif
    {%- else %}
    RegisterParameter(definition, "{{v.display}}", "", {{v.attributes.min}}f, {{v.attributes.max}}f, {{v.attributes.default}}f, 1.0f, 1.0f, P_{{k|upper}}, "{{v.display}}");
    {%- endif %}
    {%- endfor %}
    return numparams;
  }

  UNITY_AUDIODSP_RESULT UNITY_AUDIODSP_CALLBACK CreateCallback(UnityAudioEffectState* state) {
    EffectData* effectdata = new EffectData;
    effectdata->data.context = new Heavy_{{patch_name}}((double) state->samplerate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
    state->effectdata = effectdata;
    InitParametersFromDefinitions(InternalRegisterEffectDefinition, effectdata->data.p);
    return UNITY_AUDIODSP_OK;
  }

  UNITY_AUDIODSP_RESULT UNITY_AUDIODSP_CALLBACK ReleaseCallback(UnityAudioEffectState* state) {
    EffectData::Data* data = &state->GetEffectData<EffectData>()->data;
    delete data->context;
    delete data;
    return UNITY_AUDIODSP_OK;
  }

  UNITY_AUDIODSP_RESULT UNITY_AUDIODSP_CALLBACK SetFloatParameterCallback(
      UnityAudioEffectState* state, int index, float value) {
    EffectData::Data *data = &state->GetEffectData<EffectData>()->data;

    switch (index) {
      {%- for k, v in parameters %}
      case P_{{k|upper}}: data->context->sendFloatToReceiver(Heavy_{{patch_name}}::Parameter::In::{{k|upper}}, value); break;
      {%- endfor %}
      default: return UNITY_AUDIODSP_ERR_UNSUPPORTED;
    }

    data->p[index] = value;
    return UNITY_AUDIODSP_OK;
  }

  UNITY_AUDIODSP_RESULT UNITY_AUDIODSP_CALLBACK GetFloatParameterCallback(
        UnityAudioEffectState* state, int index, float* value, char *valuestr) {
    EffectData::Data* data = &state->GetEffectData<EffectData>()->data;
    if (index < 0 || index >= P_NUM_HV_PARAMS_) return UNITY_AUDIODSP_ERR_UNSUPPORTED;
    if (value != NULL) *value = data->p[index];
    if (valuestr != NULL) valuestr[0] = 0;
    return UNITY_AUDIODSP_OK;
  }

  int UNITY_AUDIODSP_CALLBACK GetFloatBufferCallback(UnityAudioEffectState* state,
      const char* name, float* buffer, int numsamples) {
    return UNITY_AUDIODSP_OK;
  }

  UNITY_AUDIODSP_RESULT UNITY_AUDIODSP_CALLBACK ProcessCallback(
      UnityAudioEffectState* state, float* inbuffer, float* outbuffer,
      unsigned int length, int inchannels, int outchannels) {
    EffectData::Data* data = &state->GetEffectData<EffectData>()->data;
    if (state->flags & UnityAudioEffectStateFlags_IsPaused) return UNITY_AUDIODSP_OK;
    hv_assert(inchannels == data->context->getNumInputChannels());
    hv_assert(outchannels == data->context->getNumOutputChannels());

    data->context->processInlineInterleaved(inbuffer, outbuffer, length);
    return UNITY_AUDIODSP_OK;
  }
}
