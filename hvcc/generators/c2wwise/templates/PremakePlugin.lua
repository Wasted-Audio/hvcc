if not _AK_PREMAKE then
    error('You must use the custom Premake5 scripts by adding the following parameter: --scripts="Scripts\\Premake"', 1)
end

local Plugin = {}
Plugin.name = "{{name}}"
Plugin.factoryheader = "../SoundEnginePlugin/{{name}}{{plugin_type}}Factory.h"
Plugin.sdk = {}
Plugin.sdk.static = {}
Plugin.sdk.shared = {}
Plugin.authoring = {}

Plugin.sdk.static.includedirs = {}
Plugin.sdk.static.files =
{
    "**.cpp",
    "**.h",
    "**.hpp",
    "**.c",
}
Plugin.sdk.static.excludes =
{
    "{{name}}{{plugin_type}}Shared.cpp"
}
Plugin.sdk.static.links = {}
Plugin.sdk.static.libsuffix = "{{plugin_type}}"
Plugin.sdk.static.libdirs = {}
Plugin.sdk.static.defines = {}
Plugin.sdk.static.custom = function()
   filter "system:Windows"
      systemversion "10.0.19041.0"
end

Plugin.sdk.shared.includedirs = {}
Plugin.sdk.shared.files =
{
    "{{name}}{{plugin_type}}Shared.cpp",
    "{{name}}{{plugin_type}}Factory.h",
}
Plugin.sdk.shared.excludes = {}
Plugin.sdk.shared.links = {}
Plugin.sdk.shared.libdirs = {}
Plugin.sdk.shared.defines = {}
Plugin.sdk.shared.custom = function()
   filter "system:Windows"
      systemversion "10.0.19041.0"
end

Plugin.authoring.includedirs =
{
    "../Includes",
    path.join(_AK_SDK_ROOT, "samples/Common/")
}
Plugin.authoring.files =
{
    "**.cpp",
    "**.h",
    "**.hpp",
    "**.c",
    "{{name}}.def",
    "{{name}}.xml",
    "{{name}}.rc",
}
Plugin.authoring.excludes = {}
Plugin.authoring.links = {}
Plugin.authoring.libdirs = {}
Plugin.authoring.defines = {}
Plugin.authoring.custom = function()
   filter "system:Windows"
      systemversion "10.0.19041.0"
end

return Plugin
