{{copyright}}

#include <locale>
#include <codecvt>
#include <iostream>
#include <fstream>

#include "stdafx.h"
#include <AK/Tools/Common/AkAssert.h>
#include <AK/Tools/Common/AkFNVHash.h>
#include <libnyquist/WavDecoder.h>
#include <libnyquist/WavEncoder.h>

#include "Hv_{{name}}_WwiseAuthoringPlugin.h"
#include "Hv_{{name}}_WwiseResource.h"
#include "Hv_{{name}}_WwisePluginIDs.h"

DEFINE_PLUGIN_REGISTER_HOOK

/** Table of display name resources (one for each property). */
struct DisplayNameInfo {
  LPCWSTR wszPropName;
  UINT uiDisplayName;
};

static DisplayNameInfo g_DisplayNames[] = {
  {%- for k, v in parameters %}
  { L"{{v.display}}", IDS_HV_PARAM_{{k|upper}} },
  {%- endfor %}
  { NULL, NULL }
};

// These IDs must be the same as those specified in the plug-in's XML definition file.
// Note that there are restrictions on the values you can use for CompanyID, and PluginID
// must be unique for the specified CompanyID. Furthermore, these IDs are persisted
// in project files. NEVER CHANGE THEM or existing projects will not recognize this Plug-in.
// Be sure to read the SDK documentation regarding Plug-ins XML definition files.
const short Hv_{{name}}_WwiseAuthoringPlugin::CompanyID = HV_COMPANY_ID;
const short Hv_{{name}}_WwiseAuthoringPlugin::PluginID = HV_{{name|upper}}_PLUGIN_ID;

Hv_{{name}}_WwiseAuthoringPlugin::Hv_{{name}}_WwiseAuthoringPlugin(AkUInt16 in_idPlugin) {
  m_pObjectMedia = nullptr;
  m_pPSet = nullptr;
  m_hwndPropView = nullptr;
  m_hwndObjPane = nullptr;
  m_idDialogBig = IDD_HV_{{name|upper}}_PLUGIN_BIG;
  m_idDialogSmall = IDD_HV_{{name|upper}}_PLUGIN_SMALL;
}

void Hv_{{name}}_WwiseAuthoringPlugin::Destroy() {
  delete this;
}

AK::Wwise::IPluginMediaConverter* Hv_{{name}}_WwiseAuthoringPlugin::GetPluginMediaConverterInterface() {
  return this;
}

AK::Wwise::ConversionResult Hv_{{name}}_WwiseAuthoringPlugin::ConvertFile(const GUID & in_guidPlatform,
    const BasePlatformID &in_basePlatform, LPCWSTR in_szSourceFile, LPCWSTR in_szDestFile,
    AkUInt32 in_uSampleRate, AkUInt32 in_uBlockLength, AK::Wwise::IProgress* in_pProgress,
    AK::Wwise::IWriteString* io_pError) {

  if (wcslen(in_szSourceFile) > 0) {
    // convert input file to 32bit floating point wav
    nqr::NyquistIO loader;
    std::shared_ptr<nqr::AudioData> fileData = std::make_shared<nqr::AudioData>();
    std::string inPath = std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(in_szSourceFile);
    loader.Load(fileData.get(), inPath);

    std::string outPath = std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(in_szDestFile);
    nqr::WavEncoder::WriteFile({ 1, nqr::PCM_FLT, nqr::DITHER_NONE }, fileData.get(), outPath);
  } else {
    // Note(joe): because we create dummy media sources for the patch tables the input file here doesn't exist
    // but we still need to create a dummy output file to avoid errors
    std::ofstream outfile(in_szDestFile);
    outfile.close();
  }
  return AK::Wwise::ConversionSuccess;
}

ULONG Hv_{{name}}_WwiseAuthoringPlugin::GetCurrentConversionSettingsHash(const GUID & in_guidPlatform,
    AkUInt32 in_uSampleRate, AkUInt32 in_uBlockLength) {
  AK::FNVHash32 hashFunc;

  // Generate a Hash from effect parameters that have an influence on the conversion
  // Take the source file name
  CString szInputFileName;
  m_pObjectMedia->GetMediaSourceFileName(szInputFileName.GetBuffer(_MAX_PATH), _MAX_PATH);
  szInputFileName.ReleaseBuffer();
  szInputFileName.MakeLower();
  return hashFunc.Compute((unsigned char *) (LPCTSTR) szInputFileName, szInputFileName.GetLength()*sizeof(TCHAR));
}

void Hv_{{name}}_WwiseAuthoringPlugin::SetPluginPropertySet(AK::Wwise::IPluginPropertySet *in_pPSet) {
  m_pPSet = in_pPSet;
}

void Hv_{{name}}_WwiseAuthoringPlugin::InitToDefault() {
  {% if tables|length > 0 -%}
  // initialise plugin with dummy media files for each table on load
  {%- for k, v in tables %}
  m_pObjectMedia->SetMediaSource(nullptr, {{loop.index-1}}, false); // '{{v.display}}'
  {%- endfor %}
  {%- endif %}
}

void Hv_{{name}}_WwiseAuthoringPlugin::SetPluginObjectMedia(AK::Wwise::IPluginObjectMedia *in_pObjectMedia) {
  m_pObjectMedia = in_pObjectMedia;
}

void Hv_{{name}}_WwiseAuthoringPlugin::NotifyPluginMediaChanged() {
  m_pPSet->NotifyInternalDataChanged(AK::IAkPluginParam::ALL_PLUGIN_DATA_ID);
}

HINSTANCE Hv_{{name}}_WwiseAuthoringPlugin::GetResourceHandle() const {
  return AfxGetStaticModuleState()->m_hCurrentResourceHandle;
}

bool Hv_{{name}}_WwiseAuthoringPlugin::GetDialog(eDialog in_eDialog,
    UINT &out_uiDialogID, AK::Wwise::PopulateTableItem *&out_pTable) const {
  // Determine what dialog just get called and set the property names to
  // UI control binding populated table.
  CComVariant varProp;

  switch (in_eDialog) {
    case SettingsDialog: {
      out_uiDialogID = m_idDialogBig;
      out_pTable = nullptr;
      return true;
    }
    case ContentsEditorDialog: {
      out_uiDialogID = m_idDialogSmall;
      out_pTable = nullptr;
      return true;
    }
    default: return false;
  }
}

bool Hv_{{name}}_WwiseAuthoringPlugin::WindowProc(eDialog in_eDialog,
    HWND in_hWnd, UINT in_message, WPARAM in_wParam, LPARAM in_lParam,
    LRESULT &out_lResult) {
  // Standard window function, user can intercept what ever message that is
  // of interest to him to implement UI behavior.
  switch (in_message) {
    case WM_INITDIALOG: {
      if (in_eDialog == ContentsEditorDialog) {
        m_hwndObjPane = in_hWnd;
      }
      else if (in_eDialog == SettingsDialog) {
        m_hwndPropView = in_hWnd;

        {% if (parameters|length + sends|length + tables|length) > 10 -%}
        RECT rect;
        if (GetClientRect(in_hWnd, &rect)) {
          // Create Scrollbar
          CreateWindowEx(0,
            L"SCROLLBAR",
            (PTSTR) NULL,
            WS_CHILD | WS_VISIBLE | SBS_VERT | SBS_RIGHTALIGN,
            rect.left,
            rect.top,
            rect.right,
            rect.bottom - GetSystemMetrics(SM_CYVTHUMB), // thumbwidth
            in_hWnd,
            (HMENU) NULL,
            GetResourceHandle(),
            (PVOID) NULL);

          SCROLLINFO si = {0};
          si.cbSize = sizeof(SCROLLINFO);
          si.fMask = SIF_ALL;
          si.nMin = 0;
          si.nMax = 2500;
          si.nPage = (rect.bottom - rect.top);
          si.nPos = 0;
          si.nTrackPos = 0;
          SetScrollInfo(in_hWnd, SB_VERT, &si, true);

          m_scrollPos = 0;
        }
        {%- endif %}
      }
      break;
    }

    {% if (parameters|length + sends|length + tables|length) > 10 -%}
    case WM_SIZE: {
      break;
    }

    case WM_VSCROLL: {
      auto action = LOWORD(in_wParam);
      HWND hScroll = (HWND) in_lParam;
      int pos = -1;
      if (action == SB_THUMBPOSITION || action == SB_THUMBTRACK) {
        pos = HIWORD(in_wParam);
      }
      else if (action == SB_LINEDOWN) {
        pos = m_scrollPos + 30;
      }
      else if (action == SB_LINEUP) {
        pos = m_scrollPos - 30;
      }
      if (pos == -1) {
        break;
      }

      SCROLLINFO si = {0};
      si.cbSize = sizeof(SCROLLINFO);
      si.fMask = SIF_POS;
      si.nPos = pos;
      si.nTrackPos = 0;
      SetScrollInfo(in_hWnd, SB_VERT, &si, true);
      GetScrollInfo(in_hWnd, SB_VERT, &si);
      pos = si.nPos;
      POINT pt;
      pt.x = 0;
      pt.y = pos - m_scrollPos;
      auto hdc = GetDC(in_hWnd);
      LPtoDP(hdc, &pt, 1);
      ReleaseDC(in_hWnd, hdc);
      ScrollWindow(in_hWnd, 0, -pt.y, NULL, NULL);
      m_scrollPos = pos;

      break;
    }
    {%- endif %}

    case WM_DESTROY: {
      if (in_eDialog == SettingsDialog) {
        m_hwndPropView = nullptr;
      } else if ( in_eDialog == ContentsEditorDialog ) {
        m_hwndObjPane = nullptr;
      }
      break;
    }

    // Catch window command actions (regardless if it is object pane or property
    // view) to enable/disable controls
    case WM_COMMAND: {
      {%- if tables|length > 0 %}
      // catch button clicks
      switch (HIWORD(in_wParam)) {
        case BN_CLICKED: {
          switch (LOWORD(in_wParam)) {
            {%- for k, v in tables %}
            case IDC_BUTTON_HV_TABLE_{{k|upper}}: return SaveAudioFileToTableId({{loop.index-1}}); // {{v.display}}
            {%- endfor %}
            default: break;
          }
        }
        default: break;
      }
      {%- endif %}
      break;
    }

    case WM_ENABLE: {
      // Enable/Disable all child controls
      HWND hWnd = ::GetWindow(in_hWnd, GW_CHILD);
      while(hWnd) {
        ::EnableWindow(hWnd, in_wParam == TRUE);
        hWnd = ::GetWindow(hWnd, GW_HWNDNEXT);
      }
      return true;
    }
  }
  out_lResult = 0;
  return false;
}

// Store current plugin settings into banks when asked to.
bool Hv_{{name}}_WwiseAuthoringPlugin::GetBankParameters(const GUID &in_guidPlatform,
    AK::Wwise::IWriteData *in_pDataWriter) const {
  CComVariant varProp;

  {%- for k, v in parameters %}
  m_pPSet->GetValue(in_guidPlatform, szHv_{{name}}_Param_{{k}}, varProp);
  in_pDataWriter->WriteReal32(varProp.fltVal);
  {%- endfor %}

  return true;
}

bool Hv_{{name}}_WwiseAuthoringPlugin::Help(
    HWND in_hWnd, eDialog in_eDialog, LPCWSTR in_szLanguageCode) const {
  return false;
};

bool Hv_{{name}}_WwiseAuthoringPlugin::SaveAudioFileToTableId(unsigned int tableId) {
  static TCHAR BASED_CODE szFilter[] = _T("Audio Files (*.wav)|*.wav|");
  CFileDialog dialog(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, szFilter);
  if (dialog.DoModal() == IDOK) {
    m_pObjectMedia->SetMediaSource(dialog.GetPathName(), tableId, true);
    return true;
  }
  return false;
};
{# force new line #}
