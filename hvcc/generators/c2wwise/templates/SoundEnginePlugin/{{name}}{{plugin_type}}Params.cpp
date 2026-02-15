{{copyright}}

#include "{{name}}{{plugin_type}}Params.h"

#include <AK/Tools/Common/AkBankReadHelpers.h>

{{name}}{{plugin_type}}Params::{{name}}{{plugin_type}}Params(const {{name}}{{plugin_type}}Params& in_rParams)
{
{% if parameters|length > 0 %}
    RTPC = in_rParams.RTPC;
    m_paramChangeHandler.SetAllParamChanges();
{% endif %}
}

AK::IAkPluginParam* {{name}}{{plugin_type}}Params::Clone(AK::IAkPluginMemAlloc* in_pAllocator)
{
    return AK_PLUGIN_NEW(in_pAllocator, {{name}}{{plugin_type}}Params(*this));
}

AKRESULT {{name}}{{plugin_type}}Params::Init(AK::IAkPluginMemAlloc* in_pAllocator, const void* in_pParamsBlock, AkUInt32 in_ulBlockSize)
{
    if (in_ulBlockSize == 0)
    {
{%- for k, v in parameters %}
        RTPC.{{k}} = {{v.attributes.default}};
{%- endfor %}
{% if parameters|length > 0 %}
        m_paramChangeHandler.SetAllParamChanges();
{% endif %}
        return AK_Success;
    }

    return SetParamsBlock(in_pParamsBlock, in_ulBlockSize);
}

AKRESULT {{name}}{{plugin_type}}Params::Term(AK::IAkPluginMemAlloc* in_pAllocator)
{
    AK_PLUGIN_DELETE(in_pAllocator, this);
    return AK_Success;
}

AKRESULT {{name}}{{plugin_type}}Params::SetParamsBlock(const void* in_pParamsBlock, AkUInt32 in_ulBlockSize)
{
    AKRESULT eResult = AK_Success;
    AkUInt8* pParamsBlock = (AkUInt8*)in_pParamsBlock;

{%- for k, v in parameters %}
    RTPC.{{k}} = READBANKDATA(AkReal32, pParamsBlock, in_ulBlockSize);
{%- endfor %}
    CHECKBANKDATASIZE(in_ulBlockSize, eResult);
{% if parameters|length > 0 %}
    m_paramChangeHandler.SetAllParamChanges();
{%- endif %}

    return eResult;
}

AKRESULT {{name}}{{plugin_type}}Params::SetParam(AkPluginParamID in_paramID, const void* in_pValue, AkUInt32 in_ulParamSize)
{
    AKRESULT eResult = AK_Success;

{% if parameters|length > 0 %}
    switch (in_paramID)
    {
{%- for k, v in parameters %}
    case {{loop.index-1}}:
        {
            const float fNewValue = *((AkReal32*)in_pValue);
            const bool bChanged = RTPC.{{k}} != fNewValue;
            RTPC.{{k}} = fNewValue;
            if (bChanged)
                m_paramChangeHandler.SetParamChange({{loop.index-1}});
        } break;
{%- endfor %}
    default:
        eResult = AK_InvalidParameter;
        break;
    }
{% endif %}

    return eResult;
}
