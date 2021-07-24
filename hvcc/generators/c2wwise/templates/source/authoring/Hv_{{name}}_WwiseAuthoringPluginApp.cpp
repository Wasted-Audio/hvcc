{{copyright}}

#include "stdafx.h"
#include <AK/Wwise/Utilities.h>
#include <AK/Tools/Common/AkAssert.h>
#include "Hv_{{name}}_Wwise{{plugin_type}}PluginFactory.h"
#include "Hv_{{name}}_WwiseAuthoringPlugin.h"
#include "Hv_{{name}}_WwiseAuthoringPluginApp.h"

BEGIN_MESSAGE_MAP(Hv_{{name}}_WwiseAuthoringPluginApp, CWinApp)
END_MESSAGE_MAP()

/** Only one PluginApp should exist */
Hv_{{name}}_WwiseAuthoringPluginApp {{name}}App;

BOOL Hv_{{name}}_WwiseAuthoringPluginApp::InitInstance() {
  __super::InitInstance();
  AK::Wwise::RegisterWwisePlugin();
  return TRUE;
}

/** Plugin Creation DLL export. */
AK::Wwise::IPluginBase* __stdcall AkCreatePlugin(
    unsigned short in_usCompanyID, unsigned short in_usPluginID) {
  if (in_usCompanyID == Hv_{{name}}_WwiseAuthoringPlugin::CompanyID &&
      in_usPluginID == Hv_{{name}}_WwiseAuthoringPlugin::PluginID) {
    return new Hv_{{name}}_WwiseAuthoringPlugin(in_usPluginID);
  }
  return NULL;
}

/** Dummy assert hook for Wwise plug-ins using AKASSERT (cassert used by default). */
DEFINEDUMMYASSERTHOOK;
{# force new line #}
