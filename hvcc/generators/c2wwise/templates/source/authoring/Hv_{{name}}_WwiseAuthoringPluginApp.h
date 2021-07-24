{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_APP_H_
#define _HV_{{name|upper}}_WWISE_APP_H_

#ifndef __AFXWIN_H__
#error include 'stdafx.h' before including this file for PCH
#endif

#include "Hv_{{name}}_WwiseResource.h"   // main symbols

class Hv_{{name}}_WwiseAuthoringPluginApp : public CWinApp {
public:
  Hv_{{name}}_WwiseAuthoringPluginApp() {};

  virtual BOOL InitInstance();

  DECLARE_MESSAGE_MAP()
};

#endif // _HV_{{name|upper}}_WWISE_APP_H_
{# force new line #}
