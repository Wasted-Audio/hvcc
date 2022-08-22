{%- set isSource = true if plugin_type == "Source" -%}
{{copyright}}

#include "Hv_{{name}}_Wwise{{plugin_type}}PluginEngine.h"
#include "Hv_{{name}}_WwisePluginIDs.h"
#include "Heavy_{{name}}.hpp"
#include <AK/AkWwiseSDKVersion.h>
#include <AK/Tools/Common/AkAssert.h>
#include <AK/Tools/Common/AkFNVHash.h>

typedef struct WavHeader {
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


AK::IAkPlugin* CreateHv_{{name}}_WwisePluginEngine(AK::IAkPluginMemAlloc *in_pAllocator) {
  return AK_PLUGIN_NEW( in_pAllocator, Hv_{{name}}_WwisePluginEngine() );
}

/** Plugin mechanism. Parameters node creation function to be registered to the FX manager. */
AK::IAkPluginParam *CreateHv_{{name}}_WwisePluginEngineParams(AK::IAkPluginMemAlloc *in_pAllocator) {
  return AK_PLUGIN_NEW(in_pAllocator, Hv_{{name}}_EngineParams());
}


static void OnHeavyPrint(HeavyContextInterface *context, const char *printName, const char *str,
    const HvMessage *msg) {
  Hv_{{name}}_WwisePluginEngine *engine = reinterpret_cast<Hv_{{name}}_WwisePluginEngine *>(context->getUserData());
  if (engine != nullptr) {
    engine->PostDebugMessage(str);
  }
}
{% if sends|length > 0 %}
static void OnSendMessageCallback(HeavyContextInterface *context, const char *sendName,
    hv_uint32_t sendHash, const HvMessage *msg) {
  Hv_{{name}}_WwisePluginEngine *engine = reinterpret_cast<Hv_{{name}}_WwisePluginEngine *>(context->getUserData());
  if (engine != nullptr && hv_msg_isFloat(msg, 0)) {
    switch (sendHash) {
      {%- for k, v in sends %}
      case {{v.hash}}: engine->SetOutRTPC("{{k|lower}}", {{k|length}}, hv_msg_getFloat(msg, 0)); break;
      {%- endfor %}
      default: return;
    }
  }
}
{%- endif %}
/** Static initializer object to register automatically the plugin into the sound engine */
AK::PluginRegistration Hv_{{name}}_Wwise{{plugin_type}}PluginRegistration(
  {{ "AkPluginTypeSource" if isSource else "AkPluginTypeEffect" }},
  HV_COMPANY_ID, HV_{{name|upper}}_PLUGIN_ID,
  CreateHv_{{name}}_WwisePluginEngine,
  CreateHv_{{name}}_WwisePluginEngineParams);

Hv_{{name}}_WwisePluginEngine::Hv_{{name}}_WwisePluginEngine() {
  /** Initialize members. */
  m_pPluginContext = NULL;
  m_pEngineParams = NULL;
  m_pHeavyContext = NULL;
  m_uSampleRate = 0;

  {%- for k, v in parameters %}
  m_fPrevParam_{{k}} = {{v.attributes.default}}f;
  {%- endfor %}
}

Hv_{{name}}_WwisePluginEngine::~Hv_{{name}}_WwisePluginEngine() {

}

AKRESULT Hv_{{name}}_WwisePluginEngine::Init(AK::IAkPluginMemAlloc *in_pAllocator,
    AK::{{ "IAkSourcePluginContext" if isSource else "IAkEffectPluginContext" }} *in_pPluginContext, AK::IAkPluginParam *in_pParams,
    AkAudioFormat &io_rFormat) {

  m_pPluginContext = in_pPluginContext;

  AKASSERT(in_pParams != NULL);

  // Initialise Heavy context
  m_uSampleRate = io_rFormat.uSampleRate;
  m_pHeavyContext = new Heavy_{{name}}((double) m_uSampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  m_pHeavyContext->setUserData(this);
  {% if sends|length > 0 -%}
  m_pHeavyContext->setSendHook(&OnSendMessageCallback);
  {%- endif %}
#ifndef AK_OPTIMIZED
  m_pHeavyContext->setPrintHook(&OnHeavyPrint);
#endif
  {% if isSource %}
  // Notify pipeline of chosen output format change.
  AkChannelMask channelMask = (hv_getNumOutputChannels(m_pHeavyContext) > 1)
      ? AK_SPEAKER_SETUP_2_0 : AK_SPEAKER_SETUP_MONO;
  io_rFormat.channelConfig.SetStandard(channelMask);
  {% endif %}
  // Initialise Parameters
  m_pEngineParams = reinterpret_cast<Hv_{{name}}_EngineParams *>(in_pParams);
  {%- for k, v in parameters %}
  hv_sendFloatToReceiver(m_pHeavyContext, Heavy_{{name}}::Parameter::In::{{k|upper}}, m_pEngineParams->GetParam_{{k}}());
  {%- endfor %}
  {% if tables|length > 0 %}
  // Initialise tables with media
  {%- for k, v in tables %}
  LoadPluginMediaToHeavyTable({{loop.index-1}}, {{v.hash}}, hv_stringToHash("setTableSize-{{v.display}}")); // table '{{v.display}}'
  {%- endfor %}
  {% endif %}
  AK_PERF_RECORDING_RESET();

  return AK_Success;
}

AKRESULT Hv_{{name}}_WwisePluginEngine::Term(AK::IAkPluginMemAlloc *in_pAllocator) {
  delete m_pHeavyContext;
  AK_PLUGIN_DELETE(in_pAllocator, this);
  return AK_Success;
}

AKRESULT Hv_{{name}}_WwisePluginEngine::GetPluginInfo(AkPluginInfo & out_rPluginInfo) {
  out_rPluginInfo.eType = {{ "AkPluginTypeSource" if isSource else "AkPluginTypeEffect" }};
  out_rPluginInfo.bIsInPlace = true;
  out_rPluginInfo.uBuildVersion = AK_WWISESDK_VERSION_COMBINED;
  return AK_Success;
}

void Hv_{{name}}_WwisePluginEngine::Execute(AkAudioBuffer *io_pBufferOut) {
  AK_PERF_RECORDING_START( "Hv_{{name}}_Wwise{{type}}PluginEngine", 25, 30);

  // Retrieve RTPC values and send in as a message to context
  {%- for k, v in parameters %}
  AkReal32 param_{{k}} = m_pEngineParams->GetParam_{{k}}();
  if (param_{{k}} != m_fPrevParam_{{k}}) {
    hv_sendFloatToReceiver(m_pHeavyContext, Heavy_{{name}}::Parameter::In::{{k|upper}}, param_{{k}});
    m_fPrevParam_{{k}} = param_{{k}};
  }
  {%- endfor %}

  {% if not isSource -%}
  // zero-pad the rest of the buffer in case the numFrames is not a multiple of 4
  io_pBufferOut->ZeroPadToMaxFrames();
  {%- endif %}

  // Calculate num frames to process and retrieve buffer
  AkUInt16 numFramesToProcess = io_pBufferOut->MaxFrames();
  float *buffer = (float *) io_pBufferOut->GetChannel(0);
  {% if isSource %}
  m_pHeavyContext->processInline(nullptr, buffer, numFramesToProcess);
  {% else %}
  // Check for channel configuration mismatch
  if (io_pBufferOut->NumChannels() == 1 &&
    ((m_pHeavyContext->getNumInputChannels() == 2) || (m_pHeavyContext->getNumOutputChannels() == 2))) {
    float *tempBuffer[2] = { buffer, buffer };
    m_pHeavyContext->process(tempBuffer, tempBuffer, numFramesToProcess);
  } else {
    m_pHeavyContext->processInline(buffer, buffer, numFramesToProcess);
  }
  {% endif %}
  io_pBufferOut->uValidFrames = numFramesToProcess;
  {% if isSource -%}io_pBufferOut->eState = AK_DataReady;{%- endif %}

  AK_PERF_RECORDING_STOP("Hv_{{name}}_Wwise{{type}}PluginEngine", 25, 30);
}
{% if isSource %}
AkReal32 Hv_{{name}}_WwisePluginEngine::GetDuration() const {
  return 0.0f; // Infinite duration.
}

AkReal32 Hv_{{name}}_WwisePluginEngine::GetEnvelope() const {
  return 1.0f; // Normalized envelope.
}

AKRESULT Hv_{{name}}_WwisePluginEngine::StopLooping() {
  return AK_Success;
}
{% endif %}
void Hv_{{name}}_WwisePluginEngine::PostDebugMessage(const char *message) {
  m_pPluginContext->PostMonitorMessage(message, AK::Monitor::ErrorLevel::ErrorLevel_Message);
}

void Hv_{{name}}_WwisePluginEngine::LoadPluginMediaToHeavyTable(unsigned int mediaIndex,
    unsigned int tableHash, unsigned int tableSizeReceiverHash) {
  AkUInt8 *pPluginData = NULL;
  AkUInt32 uPluginDataSize;
  m_pPluginContext->GetPluginMedia(mediaIndex, pPluginData, uPluginDataSize); // retrieve stored plugin data

  if (pPluginData != NULL) {
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
    if (offsetBytes > 0 && newSizeBytes > 0) {
      // adjust table size
      const uint32_t numSamples = newSizeBytes * 8 / h.BitsPerSample;
      m_pHeavyContext->setLengthForTable(tableHash, numSamples);

      float *buffer = m_pHeavyContext->getBufferForTable(tableHash);
      if (buffer != NULL && newSizeBytes > 0) {
        // copy contents and notify respective receiver
        hv_memcpy(buffer, (float *) (pPluginData + offsetBytes), newSizeBytes);
        m_pHeavyContext->sendFloatToReceiver(tableSizeReceiverHash, (float) numSamples);
      }
    }
  }
}

void Hv_{{name}}_WwisePluginEngine::SetOutRTPC(const char *rtpcName,
    unsigned int nameLength, float value) {
  AK::FNVHash32 hashFunc;
  // Set the RTPC value for the plugin's associated gameobject.
  // Note(joe): if the plugin is on a bus the gameobject will be null and thus
  // set the global RTPC.
  m_pPluginContext->GlobalContext()->SetRTPCValue(
      hashFunc.Compute((unsigned char *) rtpcName, nameLength*sizeof(char)),
      value,
#if AK_WWISESDK_VERSION_MAJOR <= 2019
      m_pPluginContext->GetVoiceInfo()->GetGameObjectID(),
#else
      m_pPluginContext->GetGameObjectInfo()->GetGameObjectID(),
#endif
      0,
      AkCurveInterpolation_Linear,
      true); // disable interpolation, let the plugin handle it internally
}
{# force new line #}
