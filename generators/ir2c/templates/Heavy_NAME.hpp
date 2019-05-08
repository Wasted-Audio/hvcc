{{copyright}}

#ifndef _HEAVY_CONTEXT_{{name|upper}}_HPP_
#define _HEAVY_CONTEXT_{{name|upper}}_HPP_

#include <new> // for std::bad_alloc
// object includes
#include "HeavyContext.hpp"
{%- for i in include_set %}
#include "{{i}}"
{%- endfor %}

class Heavy_{{name}} : public HeavyContext {

 public:
  Heavy_{{name}}(double sampleRate, int poolKb=10, int inQueueKb=2, int outQueueKb=0);
  ~Heavy_{{name}}();

  // ensure desired alignment is achieved even for heap allocation
  void* operator new(size_t sz) {
	  printf("alignment: %d\n", alignof(Heavy_{{name}}));
    auto ptr = aligned_alloc(alignof(Heavy_{{name}}), sz);
    if(!ptr)
    {
      std::bad_alloc e;
      throw(e);
    }
    return ptr;
  }
  const char *getName() override { return "{{name}}"; }
  int getNumInputChannels() override { return {{signal.numInputBuffers}}; }
  int getNumOutputChannels() override { return {{signal.numOutputBuffers}}; }

  int process(float **inputBuffers, float **outputBuffer, int n) override;
  int processInline(float *inputBuffers, float *outputBuffer, int n) override;
  int processInlineInterleaved(float *inputBuffers, float *outputBuffer, int n) override;

  int getParameterInfo(int index, HvParameterInfo *info) override;

  {%- if externs.parameters.in|length > 0 or externs.parameters.out|length > 0 %}
  struct Parameter {
    {% if externs.parameters.in|length > 0 -%}
    struct In {
      enum ParameterIn : hv_uint32_t {
        {%- for k,v in externs.parameters.in %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}

    {%- if externs.parameters.out|length > 0 %}
    struct Out {
      enum ParameterOut : hv_uint32_t {
        {%- for k,v in externs.parameters.out %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}
  };
  {%- endif %}

  {%- if externs.events.in|length > 0 or externs.events.out|length > 0 %}
  struct Event {
    {%- if externs.events.in|length > 0 %}
    struct In {
      enum EventIn : hv_uint32_t {
        {%- for k,v in externs.events.in %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}

    {%- if externs.events.out|length > 0 %}
    struct Out {
      enum EventOut : hv_uint32_t {
        {%- for k,v in externs.events.out %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}
  };
  {%- endif %}

  {%- if externs.tables|length > 0 %}
  enum Table : hv_uint32_t {
    {%- for k,v in externs.tables %}
    {{k|upper}} = {{v.hash}}, // {{v.display}}
    {%- endfor %}
  };
  {%- endif %}

 private:
  HvTable *getTableForHash(hv_uint32_t tableHash) override;
  void scheduleMessageForReceiver(hv_uint32_t receiverHash, HvMessage *m) override;

  // static sendMessage functions
  {%- for d in decl_list %}
  static void {{d}}
  {%- endfor %}

  // objects
  {%- for d in def_list %}
  {{d}}
  {%- endfor %}
};

#endif // _HEAVY_CONTEXT_{{name|upper}}_HPP_
{# force newline #}
