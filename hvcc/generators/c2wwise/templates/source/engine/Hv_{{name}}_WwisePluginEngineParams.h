{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_PARAMS_H_
#define _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_PARAMS_H_

#include <AK/SoundEngine/Common/IAkPlugin.h>
#include <AK/Tools/Common/AkAssert.h>

/** Generated RTPC IDs */

// Input Parameters
{%- for k, v in parameters %}
static const AkPluginParamID HV_{{name|upper}}_PARAM_IN_{{k|upper}}_ID = {{loop.index-1}};
{%- endfor %}

/** Parameters structure for this effect. */
struct Hv_{{name}}_RTPCParams {
  /** Generated Heavy Parameters */
  {%- for k, v in parameters %}
  AkReal32 fHVParam_{{k}};
  {%- endfor %}
};

/**
 * class Hv_{{name}}_EngineParams
 * Implementation of Heavy Wwise plugin shared parameters.
 */
class Hv_{{name}}_EngineParams : public AK::IAkPluginParam {
 public:
  /** Allow effect to call accessor functions for retrieving parameter values. */
  friend class Hv_{{name}}_WwisePluginEngine;

  /** Default Constructor. */
  Hv_{{name}}_EngineParams();

  /** Destructor. */
  virtual ~Hv_{{name}}_EngineParams();

  /** Copy constructor. */
  Hv_{{name}}_EngineParams(const Hv_{{name}}_EngineParams &in_rCopy);

  /** Create duplicate. */
  virtual IAkPluginParam *Clone(AK::IAkPluginMemAlloc *in_pAllocator);

  /** Parameters node initialization. */
  virtual AKRESULT Init(AK::IAkPluginMemAlloc *in_pAllocator, const void *in_pParamsBlock,
      AkUInt32 in_uBlockSize);

  /** Terminate. */
  virtual AKRESULT Term(AK::IAkPluginMemAlloc *in_pAllocator);

  /** Set all parameters at once. */
  virtual AKRESULT SetParamsBlock(const void * in_pParamsBlock,
      AkUInt32 in_uBlockSize);

  /** Update one parameter. */
  virtual AKRESULT SetParam(AkPluginParamID in_ParamID, const void *in_pValue,
      AkUInt32 in_uParamSize);

private:
  /** Hide assignment operator. */
  Hv_{{name}}_EngineParams &operator=(const Hv_{{name}}_EngineParams &in_rCopy) = default;

  /** RTPC'd Heavy Parameter Getter Methods */
  {%- for k, v in parameters %}
  AkReal32 GetParam_{{k}}();
  {%- endfor %}

  /** RTPC Parameter structure. */
  Hv_{{name}}_RTPCParams m_Params;
};

/** Getter methods for generated Heavy parameters */
{%- for k, v in parameters %}
inline AkReal32 Hv_{{name}}_EngineParams::GetParam_{{k}}() {
  AkReal32 fParam_{{k}} = m_Params.fHVParam_{{k}};
  AKASSERT(fParam_{{k}} >= {{v.attributes.min}} && fParam_{{k}} <= {{v.attributes.max}});
  return fParam_{{k}};
}
{% endfor %}

#endif // _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_PARAMS_H_
{# force new line #}
