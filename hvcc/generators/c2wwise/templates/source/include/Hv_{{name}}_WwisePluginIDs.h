{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_PLUGIN_IDS_H_
#define _HV_{{name|upper}}_WWISE_PLUGIN_IDS_H_

#include <AK/SoundEngine/Common/AkTypes.h>

// This ID must be the same as the PluginID in the Plug-in's XML definition file
// and is persisted in project files.
// Note: Don't change the ID or existing projects will not recognize this plug-in anymore.
const AkUInt32 HV_COMPANY_ID = 64;
const AkUInt32 HV_{{name|upper}}_PLUGIN_ID = {{plugin_id}};

#endif // _HV_{{name|upper}}_WWISE_PLUGIN_IDS_H_
{# force new line #}
