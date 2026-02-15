{{copyright}}

#ifndef {{name}}{{plugin_type}}_H
#define {{name}}{{plugin_type}}_H

#include <AK/SoundEngine/Common/IAkPlugin.h>
{%- if out_events|length > 0 %}
#include <AK/Tools/Common/AkFifoQueue.h>
{%- endif %}


class HeavyContextInterface;
struct {{name}}{{plugin_type}}Params;

class {{name}}{{plugin_type}}
    : public {{"AK::IAkSourcePlugin" if is_source else "AK::IAkInPlaceEffectPlugin"}}
{
public:
    using ContextType = {{"AK::IAkSourcePluginContext" if is_source else "AK::IAkEffectPluginContext"}};

{% if out_events|length > 0 %}
    // Note(ech): AkFifoQueue requires an allocator from AkMemoryMgr at compile time which we don't link against
    // We need a queue implementation that can inject AK::IAkPluginMemAlloc at runtime to avoid using default OS allocator
    struct SysAlloc
    {
        static AkForceInline void* Alloc(size_t in_uSize)
        {
            return malloc(in_uSize);
        }

        static AkForceInline void Free(void* in_pAddress)
        {
            free(in_pAddress);
        }
    };
{%- endif %}

    {{name}}{{plugin_type}}();
    ~{{name}}{{plugin_type}}() = default;

    AKRESULT Init(AK::IAkPluginMemAlloc* in_pAllocator, ContextType* in_pContext, AK::IAkPluginParam* in_pParams, AkAudioFormat& in_rFormat) override;
    AKRESULT Term(AK::IAkPluginMemAlloc* in_pAllocator) override;
    AKRESULT Reset() override;
    AKRESULT GetPluginInfo(AkPluginInfo& out_rPluginInfo) override;
    void Execute(AkAudioBuffer* io_pBuffer) override;
{%- if is_source %}
    virtual AkReal32 GetDuration() const override { return 0.f; }
    virtual AkReal32 GetEnvelope() const override { return 1.f; }
    virtual AKRESULT StopLooping() override { return AK_Success; }
{%- else %}
    AKRESULT TimeSkip(AkUInt32 in_uFrames) override { return AK_Success; }
{%- endif %}

{% if out_events|length > 0 %}
    // Holds event IDs until global callback
    AkFifoQueue<uint32_t, 0, SysAlloc> m_EventQueue;
{%- endif %}

    AK::IAkPluginContextBase* m_pWwiseCtx;
    HeavyContextInterface *m_pHeavyCtx; // Main Heavy patch context
    {{name}}{{plugin_type}}Params* m_pParams;
    uint32_t m_uSampleRate;
};

#endif // {{name}}{{plugin_type}}_H
