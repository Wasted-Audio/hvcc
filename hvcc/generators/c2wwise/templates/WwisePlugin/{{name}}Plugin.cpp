{{copyright}}

#include "{{name}}Plugin.h"
#include "../SoundEnginePlugin/{{name}}{{plugin_type}}Factory.h"

#include "libnyquist/WavDecoder.h"
#include "libnyquist/WavEncoder.h"

#include <locale>
#include <codecvt>
#include <iostream>
#include <fstream>

bool {{name}}Plugin::GetBankParameters(const GUID & in_guidPlatform, AK::Wwise::Plugin::DataWriter& in_dataWriter) const
{
    {%- for k, v in parameters %}
    in_dataWriter.WriteReal32(m_propertySet.GetReal32(in_guidPlatform, "{{k}}"));
    {%- endfor %}

    return true;
}

void {{name}}Plugin::NotifyPluginMediaChanged()
{
    m_host.NotifyInternalDataChanged(AK::IAkPluginParam::ALL_PLUGIN_DATA_ID, true);
}

AK::Wwise::Plugin::ConversionResult {{name}}Plugin::ConvertFile(
    const GUID& in_guidPlatform,
    const BasePlatformID& in_basePlatform,
    const AkOSChar* in_szSourceFile,
    const AkOSChar* in_szDestFile,
    AkUInt32 in_uSampleRate,
    AkUInt32 in_uBlockLength,
    AK::Wwise::Plugin::IProgress* in_pProgress,
    AK::Wwise::Plugin::IWriteString* io_pError) const
{
    if (wcslen(in_szSourceFile) > 0)
    {
        // convert input file to 32bit floating point wav
        nqr::NyquistIO loader;
        std::shared_ptr<nqr::AudioData> fileData = std::make_shared<nqr::AudioData>();
        std::string inPath = std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(in_szSourceFile);
        loader.Load(fileData.get(), inPath);

        std::string outPath = std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(in_szDestFile);
        nqr::WavEncoder::WriteFile({ 1, nqr::PCM_FLT, nqr::DITHER_NONE }, fileData.get(), outPath);
    }
    else
    {
        // Note(joe): because we create dummy media sources for the patch tables the input file here doesn't exist
        // but we still need to create a dummy output file to avoid errors
        std::ofstream outFile(in_szDestFile);
        outFile.close();
    }
    return AK::Wwise::Plugin::ConversionSuccess;
}

uint32_t {{name}}Plugin::GetCurrentConversionSettingsHash(
    const GUID& in_guidPlatform,
    AkUInt32 in_uSampleRate,
    AkUInt32 in_uBlockLength) const
{
    const auto numMedia = m_objectMedia.GetMediaSourceCount();
    uint32_t hash = in_uSampleRate ^ in_uBlockLength;
    AK::FNVHash32 hashFunc;
    AkOSChar szMediaFileName[_MAX_PATH];

    for (int32_t mediaIdx = 0; mediaIdx < numMedia; ++mediaIdx)
    {
        const uint32_t fileNameSize = m_objectMedia.GetMediaSourceFileName(szMediaFileName, _MAX_PATH, mediaIdx);
        if (fileNameSize > 0)
        {
            for (int i = 0; i < fileNameSize; ++i)
            {
                szMediaFileName[i] = tolower(szMediaFileName[i]);
            }
            hash = hash * 31 + static_cast<uint32_t>(hashFunc.Compute(szMediaFileName, fileNameSize));
        }
    }

    return hash;
}

DEFINE_AUDIOPLUGIN_CONTAINER({{name}});
EXPORT_AUDIOPLUGIN_CONTAINER({{name}});
ADD_AUDIOPLUGIN_CLASS_TO_CONTAINER({{name}}, {{name}}Plugin, {{name}}{{plugin_type}});
DEFINE_PLUGIN_REGISTER_HOOK
DEFINEDUMMYASSERTHOOK;
