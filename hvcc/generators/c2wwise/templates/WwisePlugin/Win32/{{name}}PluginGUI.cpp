{{copyright}}

#include "{{name}}PluginGUI.h"
#include "../resource.h"
#include "stdafx.h"

using namespace AK::Wwise::Plugin;

namespace {{name}}_Private
{
    static bool SaveAudioFileToTableId(ObjectMedia& in_pObjectMedia, const uint32_t& in_uTableId)
    {
        AFX_MANAGE_STATE(AfxGetStaticModuleState());
        static TCHAR BASED_CODE szFilter[] = _T("Audio Files (*.wav)|*.wav|");
        CFileDialog Dialog(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, szFilter);
        if (Dialog.DoModal() == IDOK)
        {
            const bool bOk = in_pObjectMedia.SetMediaSource(Dialog.GetPathName(), in_uTableId, true);
            if (bOk)
            {
                in_pObjectMedia.InvalidateMediaSource(in_uTableId);
                return true;
            }
        }
        return false;
    };
}

{{name}}PluginGUI::{{name}}PluginGUI()
    : m_hwndPropView(nullptr)
    , m_hwndObjPane(nullptr)
    , m_uiBigDialogID(IDD_HV_{{name|upper}}_PLUGIN_BIG)
    , m_uiSmallDialogID(IDD_HV_{{name|upper}}_PLUGIN_SMALL)
{%- if (parameters|length + sends|length + tables|length) > 10 %}
    , m_iScrollPos(0)
{% endif -%}
{
}

bool {{name}}PluginGUI::GetDialog(eDialog in_eDialog, uint32_t& out_uiDialogID, PopulateTableItem*& out_pTable) const
{
    switch (in_eDialog) {
    case SettingsDialog:
        out_uiDialogID = m_uiBigDialogID;
        out_pTable = nullptr;
        return true;
    case ContentsEditorDialog:
        out_uiDialogID = m_uiSmallDialogID;
        out_pTable = nullptr;
        return true;
    }
    return false;
}

bool {{name}}PluginGUI::WindowProc(eDialog in_eDialog, HWND in_hWnd, uint32_t in_message, WPARAM in_wParam, LPARAM in_lParam, LRESULT& out_lResult)
{
  using namespace {{name}}_Private;

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

          m_iScrollPos = 0;
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
        pos = m_iScrollPos + 30;
      }
      else if (action == SB_LINEUP) {
        pos = m_iScrollPos - 30;
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
      pt.y = pos - m_iScrollPos;
      auto hdc = GetDC(in_hWnd);
      LPtoDP(hdc, &pt, 1);
      ReleaseDC(in_hWnd, hdc);
      ScrollWindow(in_hWnd, 0, -pt.y, NULL, NULL);
      m_iScrollPos = pos;

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
            case IDC_BUTTON_HV_TABLE_{{k|upper}}: return SaveAudioFileToTableId(m_objectMedia, {{loop.index-1}}); // {{v.display}}
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

ADD_AUDIOPLUGIN_CLASS_TO_CONTAINER(
    {{name}},
    {{name}}PluginGUI,
    {{name}}{{plugin_type}}
);
