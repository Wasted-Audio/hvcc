{{copyright}}

#include <AK/SoundEngine/Common/AkSoundEngine.h> /// Dummy assert hook definition.
#include <AK/Tools/Common/AkAssert.h>
#include "Hv_{{name}}_Wwise{{plugin_type}}PluginFactory.h"
#include "Hv_{{name}}_WwisePluginIDs.h"

DEFINE_PLUGIN_REGISTER_HOOK

// Manually define the assert hook for now as the definition of DEFINEDUMMYASSERTHOOK
// is in a file that shouldn't be linked against for console builds
AkAssertHook g_pAssertHook = NULL;
{# force new line #}
