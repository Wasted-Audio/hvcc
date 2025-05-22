{{copyright}}

#include <array>
#include "fmod.hpp"
#include "Heavy_{{name}}.hpp"

//------------------------------------------------------------------------------

enum class PluginParameterType { Float, Int, Bool };

struct PluginParameter {
  PluginParameterType type;
  union {
    float f;
    int i;
    bool b;
  };
  explicit PluginParameter(const float val) : type(PluginParameterType::Float), f(val) {}
  explicit PluginParameter(const int val)   : type(PluginParameterType::Int), i(val) {}
  explicit PluginParameter(const bool val)  : type(PluginParameterType::Bool), b(val) {}
};

//------------------------------------------------------------------------------

struct Plugin{{name|capitalize}} {
  int numInputs, numOutputs;
  std::array<PluginParameter, {{in_params|length}}> paramArray;
  std::array<hv_uint32_t, {{in_params|length}}> hashArray;
  HeavyContextInterface *ctx;
};

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginCreate(FMOD_DSP_STATE *dspState)
{
  dspState->plugindata = static_cast<Plugin{{name|capitalize}} *>(FMOD_DSP_ALLOC(dspState, sizeof(Plugin{{name|capitalize}})));

  if (!dspState->plugindata)
  {
      return FMOD_ERR_MEMORY;
  }

  int samplerate;    
  dspState->functions->getsamplerate(dspState, &samplerate);

  auto *plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);
  plugin->ctx = new Heavy_{{name}}(static_cast<double>(samplerate), {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});

  plugin->numInputs  = plugin->ctx->getNumInputChannels();
  plugin->numOutputs = plugin->ctx->getNumOutputChannels();


  {%- for param, i in in_params %}
  {%- if i.attributes.type == "float" %}
  plugin->paramArray[{{loop.index0}}] = PluginParameter({{i.attributes.default}}f);
  {%- elif i.attributes.type == "int" %}
  plugin->paramArray[{{loop.index0}}] = PluginParameter(static_cast<int>({{i.attributes.default}}));
  {%- elif i.attributes.type == "bool" %}
  plugin->paramArray[{{loop.index0}}] = PluginParameter(static_cast<bool>({{i.attributes.default}}));
  {%- endif %}
  plugin->hashArray[{{loop.index0}}] = Heavy_{{name}}::Parameter::In::{{param|upper}};
  {%- endfor %}

  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginRelease(FMOD_DSP_STATE *dspState)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);
  delete plugin->ctx;
  FMOD_DSP_FREE(dspState, plugin);
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginProcess
(
  FMOD_DSP_STATE *dspState,
  unsigned int length, 
  const FMOD_DSP_BUFFER_ARRAY *inBuffers,
  FMOD_DSP_BUFFER_ARRAY *outBuffers,
  FMOD_BOOL inputsIdle,
  FMOD_DSP_PROCESS_OPERATION op
)
{
  const auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  switch (op)
  {
  case FMOD_DSP_PROCESS_QUERY:

    if (inBuffers && outBuffers)
    {
      outBuffers[0].bufferchannelmask[0] = inBuffers[0].bufferchannelmask[0];
      outBuffers[0].speakermode = inBuffers[0].speakermode;

      {%- if is_source_plugin %}

      outBuffers[0].buffernumchannels[0] = ctx->numOutputs;
      return FMOD_OK;

      {%- else %}

      if (plugin->numInputs > 0)
      {
        if (inputsIdle)
        {
          return FMOD_ERR_DSP_DONTPROCESS;
        }
        if (inBuffers[0].buffernumchannels[0] != plugin->numInputs
        || outBuffers[0].buffernumchannels[0] != plugin->numOutputs)
        {
          return FMOD_ERR_DSP_SILENCE;
        }
      }
      {%- endif %}
    }
    break;

  case FMOD_DSP_PROCESS_PERFORM:
    if (inBuffers && outBuffers)
    {
      plugin->ctx->processInlineInterleaved(inBuffers[0].buffers[0], outBuffers[0].buffers[0], static_cast<int>(length));
    }
    break;
  }

  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginReset(FMOD_DSP_STATE *dspState)
{
  // NOTE: reset plugin state here if needed
  // auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginSetFloat
(
  FMOD_DSP_STATE *dspState,
  int idx,
  float val
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Float)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  plugin->paramArray[idx].f = val;
  plugin->ctx->sendFloatToReceiver(plugin->hashArray[idx], val);
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginGetFloat
(
  FMOD_DSP_STATE *dspState,
  int idx,
  float *outVal,
  char *outValStr
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Float)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  *outVal = plugin->paramArray[idx].f;
  if (outValStr)
  {
    snprintf(outValStr, FMOD_DSP_GETPARAM_VALUESTR_LENGTH, "%.1f", plugin->paramArray[idx].f);
  }
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginSetInt
(
  FMOD_DSP_STATE *dspState,
  int idx,
  int val
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Int)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  plugin->paramArray[idx].i = val;
  plugin->ctx->sendFloatToReceiver(plugin->hashArray[idx], static_cast<float>(val));
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginGetInt
(
  FMOD_DSP_STATE *dspState,
  int idx,
  int *outVal,
  char *outValStr
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Int)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  *outVal = plugin->paramArray[idx].i;
  if (outValStr)
  {
    snprintf(outValStr, FMOD_DSP_GETPARAM_VALUESTR_LENGTH, "%d", plugin->paramArray[idx].i);
  }
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginSetBool(
  FMOD_DSP_STATE *dspState,
  int idx,
  FMOD_BOOL val
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Bool)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  plugin->paramArray[idx].b = static_cast<bool>(val);
  plugin->ctx->sendFloatToReceiver(plugin->hashArray[idx], static_cast<float>(val));
  return FMOD_OK;
}

//------------------------------------------------------------------------------

static FMOD_RESULT F_CALL PluginGetBool(
  FMOD_DSP_STATE *dspState,
  int idx,
  int *outVal,
  char *outValStr
)
{
  auto plugin = static_cast<Plugin{{name|capitalize}} *>(dspState->plugindata);

  if (idx >= plugin->paramArray.size()
  || plugin->paramArray[idx].type != PluginParameterType::Bool)
  {
    return FMOD_ERR_INVALID_PARAM;
  }

  *outVal = static_cast<FMOD_BOOL>(plugin->paramArray[idx].b);
  if (outValStr)
  {
    snprintf(outValStr, FMOD_DSP_GETPARAM_VALUESTR_LENGTH, "%d", plugin->paramArray[idx].b);
  }
  return FMOD_OK;
}

//------------------------------------------------------------------------------

extern "C"
{
  F_EXPORT FMOD_DSP_DESCRIPTION *F_CALL FMODGetDSPDescription()
  {
    {%- for param, i in in_params %}
    static FMOD_DSP_PARAMETER_DESC param_{{param}};
    {%- endfor %}

    static FMOD_DSP_PARAMETER_DESC *param_desc[{{in_params|length}}] = {
      {%- for param, i in in_params %}
      &param_{{param}},
      {%- endfor %}
    };

    {%- for param, i in in_params %}
    {%- if i.attributes.type == "float" %}

    FMOD_DSP_INIT_PARAMDESC_FLOAT(param_{{param}}, "{{i.display}}", "", "{{i.display}}",
      {{i.attributes.min}}f, {{i.attributes.max}}f, {{i.attributes.default}}f);

    {%- elif i.attributes.type == "int" %}

    FMOD_DSP_INIT_PARAMDESC_INT(param_{{param}}, "{{i.display}}", "", "{{i.display}}",
      {{i.attributes.min}}, {{i.attributes.max}}, {{i.attributes.default}}, false, nullptr);

    {%- elif i.attributes.type == "bool" %}

    FMOD_DSP_INIT_PARAMDESC_BOOL(param_{{param}}, "{{i.display}}", "", "{{i.display}}",
      {{i.attributes.default}}, nullptr);

    {%- endif %}
    {%- endfor %}

    static FMOD_DSP_DESCRIPTION desc { FMOD_PLUGIN_SDK_VERSION, "{{name}}", 1};
    desc.numinputbuffers    = {{"0" if is_source_plugin else "1"}}; 
    desc.numoutputbuffers   = 1;
    desc.create             = PluginCreate;
    desc.release            = PluginRelease;
    desc.reset              = PluginReset;
    desc.process            = PluginProcess;
    desc.numparameters      = {{in_params|length}};
    desc.paramdesc          = param_desc;
    desc.setparameterfloat  = PluginSetFloat;
    desc.getparameterfloat  = PluginGetFloat;
    desc.setparameterint    = PluginSetInt;
    desc.getparameterint    = PluginGetInt;
    desc.setparameterbool   = PluginSetBool;
    desc.getparameterbool   = PluginGetBool;

    return &desc;
  }
}

//------------------------------------------------------------------------------

