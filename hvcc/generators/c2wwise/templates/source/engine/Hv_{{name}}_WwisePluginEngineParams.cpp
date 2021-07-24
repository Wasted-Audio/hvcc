{{copyright}}

#include "Hv_{{name}}_WwisePluginEngineParams.h"
#include <AK/Tools/Common/AkBankReadHelpers.h>

Hv_{{name}}_EngineParams::Hv_{{name}}_EngineParams() {

}

Hv_{{name}}_EngineParams::Hv_{{name}}_EngineParams(const Hv_{{name}}_EngineParams & in_rCopy) {
  m_Params = in_rCopy.m_Params;
}

Hv_{{name}}_EngineParams::~Hv_{{name}}_EngineParams() {

}

AK::IAkPluginParam * Hv_{{name}}_EngineParams::Clone(AK::IAkPluginMemAlloc *in_pAllocator) {
  return AK_PLUGIN_NEW(in_pAllocator, Hv_{{name}}_EngineParams(*this));
}

AKRESULT Hv_{{name}}_EngineParams::Init(
    AK::IAkPluginMemAlloc *in_pAllocator, const void *in_pParamsBlock, AkUInt32 in_uBlockSize) {
  if (in_uBlockSize == 0) {
    // Init with default values if we got invalid parameter block.
    // Generated RTPCs
    {%- for k, v in parameters %}
    m_Params.fHVParam_{{k}} = {{v.attributes.default}}f;
    {%- endfor %}

    return AK_Success;
  }

  return SetParamsBlock(in_pParamsBlock, in_uBlockSize);
}

AKRESULT Hv_{{name}}_EngineParams::Term(
    AK::IAkPluginMemAlloc *in_pAllocator) {
  AK_PLUGIN_DELETE(in_pAllocator, this);
  return AK_Success;
}

AKRESULT Hv_{{name}}_EngineParams::SetParamsBlock(
    const void *in_pParamsBlock, AkUInt32 in_ulBlockSize) {

  AKRESULT eResult = AK_Success;
  AkUInt8 *pParamsBlock = (AkUInt8 *) in_pParamsBlock;

  // Retrieve generated Heavy parameters
  {%- for k, v in parameters %}
  m_Params.fHVParam_{{k}} = READBANKDATA(AkReal32, pParamsBlock, in_ulBlockSize);
  {%- endfor %}

  CHECKBANKDATASIZE(in_ulBlockSize, eResult);

  return eResult;
}

AKRESULT Hv_{{name}}_EngineParams::SetParam(AkPluginParamID in_ParamID,
  const void *in_pValue, AkUInt32 in_uParamSize) {
  if (in_pValue == NULL) return AK_InvalidParameter; // Consistency check

  // Set parameter value.
  switch (in_ParamID) {
    {%- for k, v in parameters %}
    case HV_{{name|upper}}_PARAM_IN_{{k|upper}}_ID: {
      // This parameter is RTPCed
      m_Params.fHVParam_{{k}} = *reinterpret_cast<const AkReal32*>(in_pValue);
      break;
    }
    {%- endfor %}
    default: AKASSERT(!"Unknown parameter"); break;
  }

  return AK_Success;
}
{# force new line #}
