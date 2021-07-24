{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_PLUGIN_H_
#define _HV_{{name|upper}}_WWISE_PLUGIN_H_

#include <AK/Wwise/AudioPlugin.h>

/**
 * Plugin property names
 * NOTE: These should be named the same as the respective Property Name value
 * in the plugin xml definition
 */
{%- for k, v in parameters %}
static LPCWSTR szHv_{{name}}_Param_{{k}} = L"{{k}}";
{%- endfor %}

class Hv_{{name}}_WwiseAuthoringPlugin : public AK::Wwise::DefaultAudioPluginImplementation,
                                         public AK::Wwise::IPluginMediaConverter {
public:
  Hv_{{name}}_WwiseAuthoringPlugin(AkUInt16 in_idPlugin);

  ~Hv_{{name}}_WwiseAuthoringPlugin() {};

  /** AK::Wwise::IPluginBase Overrides */
  virtual void Destroy(); // Implement the destruction of the Wwise source plugin.

  /** AK:WWise::IPluginMediaConverter Overrides */
  virtual AK::Wwise::IPluginMediaConverter* GetPluginMediaConverterInterface() override;

  virtual AK::Wwise::ConversionResult ConvertFile(const GUID &in_guidPlatform, const BasePlatformID &in_basePlatform,
      LPCWSTR in_szSourceFile, LPCWSTR in_szDestFile, AkUInt32 in_uSampleRate, AkUInt32 in_uBlockLength,
      AK::Wwise::IProgress *in_pProgress, AK::Wwise::IWriteString *io_pError) override;

  virtual ULONG GetCurrentConversionSettingsHash(const GUID & in_guidPlatform,
    AkUInt32 in_uSampleRate, AkUInt32 in_uBlockLength) override;

  /** DefaultAudioPluginImplementation */
  virtual void InitToDefault() override;

  /** AK::Wwise::IAudioPlugin Overrides */
  virtual void SetPluginPropertySet(AK::Wwise::IPluginPropertySet * in_pPSet);

  virtual void SetPluginObjectMedia(AK::Wwise::IPluginObjectMedia *in_pObjectMedia) override;

  virtual void NotifyPluginMediaChanged() override;

  virtual void NotifyPropertyChanged(const GUID & in_guidPlatform,
      LPCWSTR in_szPropertyName) {};

  virtual HINSTANCE GetResourceHandle() const;

  virtual bool GetDialog(eDialog in_eDialog, UINT & out_uiDialogID,
      AK::Wwise::PopulateTableItem *& out_pTable) const;

  virtual bool WindowProc(eDialog in_eDialog, HWND in_hWnd, UINT in_message,
      WPARAM in_wParam, LPARAM in_lParam, LRESULT & out_lResult);

  virtual bool GetBankParameters(const GUID & in_guidPlatform,
      AK::Wwise::IWriteData* in_pDataWriter) const;

  virtual bool Help(HWND in_hWnd, eDialog in_eDialog,
      LPCWSTR in_szLanguageCode) const;

  static const short CompanyID;
  static const short PluginID;

private:
  bool SaveAudioFileToTableId(unsigned int tableId);

  AK::Wwise::IPluginPropertySet *m_pPSet;
  AK::Wwise::IPluginObjectMedia *m_pObjectMedia;
  HWND m_hwndPropView;
  HWND m_hwndObjPane;
  AkUInt16 m_idDialogBig;
  AkUInt16 m_idDialogSmall;
  {% if (parameters|length + sends|length + tables|length) > 10 -%}
  int m_scrollPos;
  {% endif -%}
};

#endif // _HV_{{name|upper}}_WWISE_PLUGIN_H_
{# force new line #}
