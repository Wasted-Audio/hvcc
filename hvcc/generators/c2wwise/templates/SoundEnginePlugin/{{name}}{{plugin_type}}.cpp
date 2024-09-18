{%- set register_send_hook = out_params|length > 0 or out_events|length > 0 -%}
{{copyright}}

#include "{{name}}{{plugin_type}}.h"
#include "{{name}}{{plugin_type}}Params.h"
#include "../{{name}}Config.h"

#include "Heavy/Heavy_{{name}}.hpp"

#include <AK/AkWwiseSDKVersion.h>
#include <AK/SoundEngine/Common/IAkPlugin.h>

namespace {{name}}_Private
{
    typedef struct WavHeader
    {
        uint32_t ChunkID; // 0
        uint32_t ChunkSize; // 4
        uint32_t Format; // 8
        uint32_t Subchunk1ID; // 12
        uint32_t Subchunk1Size; // 16
        uint16_t AudioFormat; // 20
        uint16_t NumChannels; // 22
        uint32_t SampleRate; // 24
        uint32_t ByteRate; // 28
        uint16_t BlockAlign; // 32
        uint16_t BitsPerSample; // 34
        uint32_t Subchunk2ID; // 36
        uint32_t Subchunk2Size; // 40
        uint32_t Subchunk2Data; // 44
        uint32_t Subchunk3ID; // 48
        uint32_t Subchunk3Size; // 52
        // data -> 56
    } WavHeader;

    void LoadPluginMediaToHeavyTable(AK::IAkPluginContextBase* in_pWwiseCtx, HeavyContextInterface* in_pHeavyCtx,
        uint32_t in_uMediaIndex, uint32_t in_uTableHash, uint32_t in_uTableSizeReceiverHash)
    {
        AkUInt8* pPluginData = NULL;
        AkUInt32 uPluginDataSize;
        in_pWwiseCtx->GetPluginMedia(in_uMediaIndex, pPluginData, uPluginDataSize); // retrieve stored plugin data

        if (pPluginData != NULL)
        {
            // determine wav header format
            WavHeader h;
            hv_memcpy(&h, pPluginData, sizeof(WavHeader));
            uint32_t offsetBytes = 0;
            const uint32_t dataID = 0x61746164; // 'data'
            const uint32_t factID = 0x74636166; // 'fact'
            if (h.Subchunk2ID == dataID) {
                offsetBytes = 44;
            }
            else if (h.Subchunk2ID == factID && h.Subchunk3ID == dataID) {
                offsetBytes = 56;
            }

            uint32_t newSizeBytes = uPluginDataSize - offsetBytes;
            if (offsetBytes > 0 && newSizeBytes > 0)
            {
                // adjust table size
                const uint32_t numSamples = newSizeBytes * 8 / h.BitsPerSample;
                in_pHeavyCtx->setLengthForTable(in_uTableHash, numSamples);

                float* buffer = in_pHeavyCtx->getBufferForTable(in_uTableHash);
                if (buffer != NULL && newSizeBytes > 0) {
                    // copy contents and notify respective receiver
                    hv_memcpy(buffer, (float*)(pPluginData + offsetBytes), newSizeBytes);
                    in_pHeavyCtx->sendFloatToReceiver(in_uTableSizeReceiverHash, (float)numSamples);
                }
            }
        }
    }

    static void SetOutRTPC(AK::IAkPluginContextBase* in_pCtx, const char* in_szRtpcName,  const uint32_t& in_uNameLen, const float& in_fValue)
    {
        AK::FNVHash32 HashFunc;
        const uint32_t RtpcID = HashFunc.Compute(in_szRtpcName, sizeof(char) * in_uNameLen);
        const AkGameObjectID ObjectID = in_pCtx->GetGameObjectInfo()->GetGameObjectID();
        in_pCtx->GlobalContext()->SetRTPCValue(RtpcID, in_fValue, ObjectID, 0, AkCurveInterpolation_Linear, false);
    }

{% if out_events|length > 0 %}
    static void PostOutEvent({{name}}{{plugin_type}}* in_pPlugin, const char* in_szEventName, const uint32_t& in_uNameLen)
    {
        AK::FNVHash32 HashFunc;
        const uint32_t EventID = HashFunc.Compute(in_szEventName, sizeof(char) * in_uNameLen);
        in_pPlugin->m_EventQueue.Enqueue(EventID);
    }
{% endif %}

    static void OnHeavyPrint(HeavyContextInterface* in_pHeavyCtx, const char* in_szPrintName, const char* in_szMessage, const HvMessage* in_pHvMessage)
    {
        auto* pPlugin = reinterpret_cast<{{name}}{{plugin_type}}*>(in_pHeavyCtx->getUserData());
        pPlugin->m_pWwiseCtx->PostMonitorMessage(in_szMessage, AK::Monitor::ErrorLevel::ErrorLevel_Message);
    }
{% if register_send_hook %}
    static void OnSendMessageCallback(HeavyContextInterface *in_pHeavyCtx, const char *in_szSendName, uint32_t in_uSendHash, const HvMessage *in_pHvMessage)
    {
        auto* pPlugin = reinterpret_cast<{{name}}{{plugin_type}}*>(in_pHeavyCtx->getUserData());
        if (pPlugin != nullptr && (hv_msg_isFloat(in_pHvMessage, 0) || hv_msg_isBang(in_pHvMessage, 0)))
        {
            switch (in_uSendHash)
            {
            {%- for k, v in out_params %}
            case {{v.hash}}: SetOutRTPC(pPlugin->m_pWwiseCtx, "{{k|lower}}", {{k|length}}, hv_msg_getFloat(in_pHvMessage, 0)); break;
            {%- endfor %}
            {%- for k, v in out_events %}
            case {{v.hash}}: PostOutEvent(pPlugin, "{{k|lower}}", {{k|length}}); break;
            {%- endfor %}
            default: return;
            }
        }
    }
{%- endif %}
{% if out_events|length > 0 %}
    static void OnGlobalCallback(AK::IAkGlobalPluginContext* in_pContext, AkGlobalCallbackLocation in_eLocation, void* in_pCookie)
    {
        if (in_eLocation != AkGlobalCallbackLocation_BeginRender)
            return;
        auto* pPlugin = reinterpret_cast<{{name}}{{plugin_type}}*>(in_pCookie);
        if (!pPlugin)
            return;

        const AkGameObjectID GameObjectID = pPlugin->m_pWwiseCtx->GetGameObjectInfo()->GetGameObjectID();
        uint32_t uEventID = 0;
        while (pPlugin->m_EventQueue.Dequeue(uEventID))
        {
            in_pContext->PostEventSync(uEventID, GameObjectID);
        }
    }
{%- endif %}
}

AK::IAkPlugin* Create{{name}}{{plugin_type}}(AK::IAkPluginMemAlloc* in_pAllocator)
{
    return AK_PLUGIN_NEW(in_pAllocator, {{name}}{{plugin_type}}());
}

AK::IAkPluginParam* Create{{name}}{{plugin_type}}Params(AK::IAkPluginMemAlloc* in_pAllocator)
{
    return AK_PLUGIN_NEW(in_pAllocator, {{name}}{{plugin_type}}Params());
}

AK_IMPLEMENT_PLUGIN_FACTORY({{name}}{{plugin_type}}, {{"AkPluginTypeSource" if is_source else "AkPluginTypeEffect"}}, {{name}}Config::CompanyID, {{name}}Config::PluginID)

{{name}}{{plugin_type}}::{{name}}{{plugin_type}}()
    : m_pWwiseCtx(nullptr)
    , m_pHeavyCtx(nullptr)
    , m_pParams(nullptr)
    , m_uSampleRate(0)
{
}

AKRESULT {{name}}{{plugin_type}}::Init(AK::IAkPluginMemAlloc* in_pAllocator, ContextType* in_pContext, AK::IAkPluginParam* in_pParams, AkAudioFormat& in_rFormat)
{
    using namespace {{name}}_Private;

    m_pParams = ({{name}}{{plugin_type}}Params*)in_pParams;
    m_pWwiseCtx = in_pContext;
    m_uSampleRate = in_rFormat.uSampleRate;

    // Initialise Heavy context
    m_pHeavyCtx = AK_PLUGIN_NEW(in_pAllocator, Heavy_{{name}}((double) m_uSampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}}));
    m_pHeavyCtx->setUserData(this);
{%- if register_send_hook %}
    m_pHeavyCtx->setSendHook(&OnSendMessageCallback);
{% endif %}
#ifndef AK_OPTIMIZED
    m_pHeavyCtx->setPrintHook(&OnHeavyPrint);
#endif
{% if is_source %}
    // Notify pipeline of chosen output format change.
    in_rFormat.channelConfig.SetStandard({{channel_config}});
  {% if num_output_channels > 0 %}
    if (in_rFormat.GetNumChannels() != hv_getNumOutputChannels(m_pHeavyCtx))
    {
        return AK_UnsupportedChannelConfig;
    }
  {% endif %}
{% else  %}
  {% if num_output_channels > 2 %}
    // Multi-channel plugins have string channel configuration requirementkk
    if (in_rFormat.channelConfig.uChannelMask != {{channel_config}})
    {
        m_pWwiseCtx->PostMonitorMessage("{{name}} only supports the following channel configuration {{channel_config}}", AK::Monitor::ErrorLevel_Error);
        return AK_UnsupportedChannelConfig;
    }
  {% else  %}
    if (in_rFormat.GetNumChannels() > 2)
    {
        m_pWwiseCtx->PostMonitorMessage("{{name}} only supports one and two channel bus configurations", AK::Monitor::ErrorLevel_Error);
        return AK_UnsupportedChannelConfig;
    }
  {% endif %}
{% endif %}
{%- for k, v in parameters %}
    hv_sendFloatToReceiver(m_pHeavyCtx, Heavy_{{name}}::Parameter::In::{{k|upper}}, m_pParams->RTPC.{{k}});
{%- endfor %}
{% if out_events|length > 0 %}
    m_EventQueue.Init(4);
    m_pWwiseCtx->GlobalContext()->RegisterGlobalCallback(
        {{"AkPluginTypeSource" if is_source else "AkPluginTypeEffect"}},
        {{name}}Config::CompanyID,
        {{name}}Config::PluginID,
        &OnGlobalCallback,
        AkGlobalCallbackLocation_BeginRender,
        this);
{%- endif %}
{% if tables|length > 0 %}
    // Initialise tables with media
  {%- for k, v in tables %}
    LoadPluginMediaToHeavyTable(m_pWwiseCtx, m_pHeavyCtx, {{loop.index-1}}, {{v.hash}}, hv_stringToHash("setTableSize-{{v.display}}")); // table '{{v.display}}'
  {%- endfor %}
{% endif %}
    AK_PERF_RECORDING_RESET();

    return AK_Success;
}

AKRESULT {{name}}{{plugin_type}}::Term(AK::IAkPluginMemAlloc* in_pAllocator)
{
    using namespace {{name}}_Private;
{% if out_events|length > 0 %}
    uint32_t EventID = 0;
    while  (m_EventQueue.Dequeue(EventID))
    {
        // the queue must be empty before termination
    }
    m_EventQueue.Term();
    m_pWwiseCtx->GlobalContext()->UnregisterGlobalCallback(OnGlobalCallback, AkGlobalCallbackLocation_BeginRender);
{% endif %}
    AK_PLUGIN_DELETE(in_pAllocator, m_pHeavyCtx);
    AK_PLUGIN_DELETE(in_pAllocator, this);
    return AK_Success;
}

AKRESULT {{name}}{{plugin_type}}::Reset()
{
    return AK_Success;
}

AKRESULT {{name}}{{plugin_type}}::GetPluginInfo(AkPluginInfo& out_rPluginInfo)
{
    out_rPluginInfo.eType = {{"AkPluginTypeSource" if is_source else "AkPluginTypeEffect"}};
    out_rPluginInfo.bIsInPlace = true;
	out_rPluginInfo.bCanProcessObjects = false;
    out_rPluginInfo.uBuildVersion = AK_WWISESDK_VERSION_COMBINED;
    return AK_Success;
}

void {{name}}{{plugin_type}}::Execute(AkAudioBuffer* io_pBuffer)
{
    AK_PERF_RECORDING_START("{{name}}{{plugin_type}}", 25, 30);

    // Retrieve RTPC values and send in as a message to context
{%- for k, v in parameters %}
    if (m_pParams->m_paramChangeHandler.HasChanged({{loop.index-1}}))
    {
        hv_sendFloatToReceiver(m_pHeavyCtx, Heavy_{{name}}::Parameter::In::{{k|upper}}, m_pParams->RTPC.{{k}});
        m_pParams->m_paramChangeHandler.ResetParamChange({{loop.index-1}});
    }
{%- endfor %}
{% if not is_source %}
    // zero-pad the rest of the buffer in case the numFrames is not a multiple of 4
    io_pBuffer->ZeroPadToMaxFrames();
{%- endif %}

    // Calculate num frames to process and retrieve buffer
    AkUInt16 numFramesToProcess = io_pBuffer->MaxFrames();
    float *pBuffer = (float *) io_pBuffer->GetChannel(0);
{% if is_source %}
    m_pHeavyCtx->processInline(nullptr, pBuffer, numFramesToProcess);
    io_pBuffer->eState = AK_DataReady;
{% else %}
    // Check for channel configuration mismatch
    if (io_pBuffer->NumChannels() == 1 &&
        ((m_pHeavyCtx->getNumInputChannels() == 2) || (m_pHeavyCtx->getNumOutputChannels() == 2)))
    {
        float *pTempBuffer[2] = { pBuffer, pBuffer };
        m_pHeavyCtx->process(pTempBuffer, pTempBuffer, numFramesToProcess);
    }
    else
    {
        m_pHeavyCtx->processInline(pBuffer, pBuffer, numFramesToProcess);
    }
{% endif %}
{% if num_output_channels > 0 %}
    io_pBuffer->uValidFrames = numFramesToProcess;
{% else %}
    // Edge case - a control-only plugin was built, outputting silence
    io_pBuffer->ZeroPadToMaxFrames();
{% endif %}
    AK_PERF_RECORDING_STOP("{{name}}{{plugin_type}}", 25, 30);
}
