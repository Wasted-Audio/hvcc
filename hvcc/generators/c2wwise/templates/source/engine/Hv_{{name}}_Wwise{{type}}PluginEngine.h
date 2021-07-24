{%- set isSource = true if plugin_type == "Source" -%}
{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_H_
#define _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_H_

#include "Hv_{{name}}_WwisePluginEngineParams.h"

class HeavyContextInterface;

/**
 * class Hv_{{name}}_WwisePluginEngine
 * Heavy context wrapper (source effect).
 */
class Hv_{{name}}_WwisePluginEngine : public AK::{{ "IAkSourcePlugin" if isSource else "IAkInPlaceEffectPlugin" }}
{
public:
  Hv_{{name}}_WwisePluginEngine();
  virtual ~Hv_{{name}}_WwisePluginEngine();

  // Plugin initialization
  virtual AKRESULT Init(AK::IAkPluginMemAlloc *in_pAllocator,
      AK::{{ "IAkSourcePluginContext" if isSource else "IAkEffectPluginContext" }} *in_pPluginContext,
      AK::IAkPluginParam *in_pParams,
      AkAudioFormat &io_rFormat) override;

  virtual AKRESULT Term(AK::IAkPluginMemAlloc *in_pAllocator) override;

  virtual AKRESULT Reset() override { return AK_Success; }

  virtual AKRESULT GetPluginInfo(AkPluginInfo & out_rPluginInfo) override;

  // Main processing loop
  virtual void Execute(AkAudioBuffer *io_pBuffer) override;
{% if isSource %}
  virtual AkReal32 GetDuration() const override;

  virtual AkReal32 GetEnvelope() const override;

  virtual AKRESULT StopLooping() override;
{% else %}
  // Return AK_DataReady or AK_NoMoreData, depending if there would be audio output or not at that point.
  virtual AKRESULT TimeSkip(AkUInt32 in_uFrames) override { return AK_DataReady; }
{% endif %}
  void PostDebugMessage(const char *str);

  void SetOutRTPC(const char *rtpcName, unsigned int nameLength, float value);

private:
  void LoadPluginMediaToHeavyTable(unsigned int mediaIndex, unsigned int tableHash,
      unsigned int tableSizeReceiverHash);

  AK::{{ "IAkSourcePluginContext" if isSource else "IAkEffectPluginContext" }} *m_pPluginContext; // Plugin context interface.
  Hv_{{name}}_EngineParams *m_pEngineParams; // Modified by Wwise/RTPC.
  HeavyContextInterface *m_pHeavyContext; // Main Heavy patch context
  AkUInt32 m_uSampleRate;

  // Store previous RTPC values
  {%- for k, v in parameters %}
  AkReal32 m_fPrevParam_{{k}};
  {%- endfor %}
};

#endif // _HV_{{name|upper}}_WWISE_PLUGIN_ENGINE_H_
{# force new line #}
