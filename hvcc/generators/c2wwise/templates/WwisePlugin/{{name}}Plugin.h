{{copyright}}

#pragma once

#include <AK/Wwise/Plugin.h>

class {{name}}Plugin final
    : public AK::Wwise::Plugin::AudioPlugin
    , public AK::Wwise::Plugin::RequestHost
    , public AK::Wwise::Plugin::RequestObjectMedia
    , public AK::Wwise::Plugin::MediaConverter
{
public:
    {{name}}Plugin() = default;
    ~{{name}}Plugin() = default;

    bool GetBankParameters(const GUID & in_guidPlatform, AK::Wwise::Plugin::DataWriter& in_dataWriter) const override;
    void NotifyPluginMediaChanged() override;

    AK::Wwise::Plugin::ConversionResult ConvertFile(
        const GUID& in_guidPlatform,
        const BasePlatformID& in_basePlatform,
        const AkOSChar* in_szSourceFile,
        const AkOSChar* in_szDestFile,
        AkUInt32 in_uSampleRate,
        AkUInt32 in_uBlockLength,
        AK::Wwise::Plugin::IProgress* in_pProgress,
        AK::Wwise::Plugin::IWriteString* io_pError
    ) const override;

    uint32_t GetCurrentConversionSettingsHash(
        const GUID& in_guidPlatform,
        AkUInt32 in_uSampleRate = 0,
        AkUInt32 in_uBlockLength = 0
    ) const override;
};

DECLARE_AUDIOPLUGIN_CONTAINER({{name}});	// Exposes our PluginContainer structure that contains the info for our plugin
