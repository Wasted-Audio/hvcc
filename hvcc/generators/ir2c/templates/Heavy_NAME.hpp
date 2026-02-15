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

#if __cplusplus < 201500L
  // override new to ensure desired alignment is achieved for pre-c++-17 builds
  void* operator new(size_t sz) {
    auto ptr = aligned_alloc(alignof(Heavy_{{name}}), sz);
#ifdef __EXCEPTIONS
    if(!ptr)
    {
      std::bad_alloc e;
      throw(e);
    }
#endif // __EXCEPTIONS
    return ptr;
  }
  void* operator new(size_t sz, const std::nothrow_t& nothrow_value) noexcept {
#ifdef __EXCEPTIONS
    try {
#endif // __EXCEPTIONS
      return operator new(sz);
#ifdef __EXCEPTIONS
    }
    catch (std::exception e) {
      return nullptr;
    }
#endif // __EXCEPTIONS
  }
  void* operator new(size_t sz, void* ptr) noexcept {
    return ptr;
  }
#endif
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


  /*
  * Code for expr~ implementation
  * Write out the generic header code
  */

  // per class code
  {%- for line in class_header_lines %}
  {{line}}
  {%- endfor %}

  // per object code
  {%- for line in obj_header_lines %}
  {{line}}
  {%- endfor %}


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
