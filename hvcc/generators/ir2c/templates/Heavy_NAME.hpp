{{copyright}}

#ifndef _HEAVY_CONTEXT_{{name|upper}}_HPP_
#define _HEAVY_CONTEXT_{{name|upper}}_HPP_

// object includes
#include "HeavyContext.hpp"
{%- for i in include_set %}
#include "{{i}}"
{%- endfor %}

class Heavy_{{name}} : public HeavyContext {

 public:
  Heavy_{{name}}(double sampleRate, int poolKb=10, int inQueueKb=2, int outQueueKb=0);
  ~Heavy_{{name}}();

  const char *getName() override { return "{{name}}"; }
  int getNumInputChannels() override { return {{signal.numInputBuffers}}; }
  int getNumOutputChannels() override { return {{signal.numOutputBuffers}}; }

  int process(float **inputBuffers, float **outputBuffer, int n) override;
  int processInline(float *inputBuffers, float *outputBuffer, int n) override;
  int processInlineInterleaved(float *inputBuffers, float *outputBuffer, int n) override;

  int getParameterInfo(int index, HvParameterInfo *info) override;

  {%- if externs.parameters.inParam|length > 0 or externs.parameters.outParam|length > 0 %}
  struct Parameter {
    {% if externs.parameters.inParam|length > 0 -%}
    struct In {
      enum ParameterIn : hv_uint32_t {
        {%- for k,v in externs.parameters.inParam %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}

    {%- if externs.parameters.outParam|length > 0 %}
    struct Out {
      enum ParameterOut : hv_uint32_t {
        {%- for k,v in externs.parameters.outParam %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}
  };
  {%- endif %}

  {%- if externs.events.inEvent|length > 0 or externs.events.outEvent|length > 0 %}
  struct Event {
    {%- if externs.events.inEvent|length > 0 %}
    struct In {
      enum EventIn : hv_uint32_t {
        {%- for k,v in externs.events.inEvent %}
        {{k|upper}} = {{v.hash}}, // {{v.display}}
        {%- endfor %}
      };
    };
    {%- endif %}

    {%- if externs.events.outEvent|length > 0 %}
    struct Out {
      enum EventOut : hv_uint32_t {
        {%- for k,v in externs.events.outEvent %}
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
