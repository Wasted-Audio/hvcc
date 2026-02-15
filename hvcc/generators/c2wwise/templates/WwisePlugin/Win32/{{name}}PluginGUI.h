{{copyright}}

#pragma once

#include "../{{name}}Plugin.h"

class {{name}}PluginGUI final
	: public AK::Wwise::Plugin::PluginMFCWindows<>
	, public AK::Wwise::Plugin::GUIWindows
    , public AK::Wwise::Plugin::RequestObjectMedia
{
public:
	{{name}}PluginGUI();

    bool GetDialog(AK::Wwise::Plugin::eDialog in_eDialog, uint32_t& out_uiDialogID,
        AK::Wwise::Plugin::PopulateTableItem*& out_pTable) const override;
    bool WindowProc(AK::Wwise::Plugin::eDialog in_eDialog, HWND in_hWnd, uint32_t in_message,
        WPARAM in_wParam, LPARAM in_lParam, LRESULT& out_lResult ) override;

 private:
    HWND m_hwndPropView;
    HWND m_hwndObjPane;
    const uint32_t m_uiBigDialogID;
    const uint32_t m_uiSmallDialogID;

    {% if (parameters|length + sends|length + tables|length) > 10 -%}
    int32_t m_iScrollPos;
    {% endif -%}
};
