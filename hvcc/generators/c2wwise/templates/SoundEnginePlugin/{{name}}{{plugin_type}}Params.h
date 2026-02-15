{{copyright}}
{# force new line #}
#ifndef {{name}}{{plugin_type}}Params_H
#define {{name}}{{plugin_type}}Params_H

#include <AK/SoundEngine/Common/IAkPlugin.h>
#include <AK/Plugin/PluginServices/AkFXParameterChangeHandler.h>

{% if parameters|length > 0 %}
struct {{name}}RTPCParams
{
    {%- for k, v in parameters %}
    AkReal32 {{k}} = {{v.attributes.default}};
    {%- endfor %}
};
{% endif %}

struct {{name}}{{plugin_type}}Params
    : public AK::IAkPluginParam
{
    {{name}}{{plugin_type}}Params() = default;
    {{name}}{{plugin_type}}Params(const {{name}}{{plugin_type}}Params& in_rParams);

    ~{{name}}{{plugin_type}}Params() = default;

    IAkPluginParam* Clone(AK::IAkPluginMemAlloc* in_pAllocator) override;
    AKRESULT Init(AK::IAkPluginMemAlloc* in_pAllocator, const void* in_pParamsBlock, AkUInt32 in_ulBlockSize) override;
    AKRESULT Term(AK::IAkPluginMemAlloc* in_pAllocator) override;
    AKRESULT SetParamsBlock(const void* in_pParamsBlock, AkUInt32 in_ulBlockSize) override;
    AKRESULT SetParam(AkPluginParamID in_paramID, const void* in_pValue, AkUInt32 in_ulParamSize) override;

{% if parameters|length > 0 %}
    AK::AkFXParameterChangeHandler<{{parameters|length}}> m_paramChangeHandler;
    {{name}}RTPCParams RTPC;
{% endif %}
};

#endif // {{name}}{{plugin_type}}Params_H
