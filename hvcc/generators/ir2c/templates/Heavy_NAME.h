{{copyright}}

#ifndef _HEAVY_{{name|upper}}_H_
#define _HEAVY_{{name|upper}}_H_

#include "HvHeavy.h"

#ifdef __cplusplus
extern "C" {
#endif

#if HV_APPLE
#pragma mark - Heavy Context
#endif

{% if externs.parameters.in|length > 0 -%}
typedef enum {
  {%- for k,v in externs.parameters.in %}
  HV_{{name|upper}}_PARAM_IN_{{k|upper}} = {{v.hash}}, // {{v.display}}
  {%- endfor %}
} Hv_{{name}}_ParameterIn;
{% endif -%}

{% if externs.parameters.out|length > 0 %}
typedef enum {
  {%- for k,v in externs.parameters.out %}
  HV_{{name|upper}}_PARAM_OUT_{{k|upper}} = {{v.hash}}, // {{v.display}}
  {%- endfor %}
} Hv_{{name}}_ParameterOut;
{% endif -%}

{% if externs.events.in|length > 0 %}
typedef enum {
  {%- for k,v in externs.events.in %}
  HV_{{name|upper}}_EVENT_IN_{{k|upper}} = {{v.hash}}, // {{v.display}}
  {%- endfor %}
} Hv_{{name}}_EventIn;
{% endif -%}

{% if externs.events.out|length > 0 %}
typedef enum {
  {%- for k,v in externs.events.out %}
  HV_{{name|upper}}_EVENT_OUT_{{k|upper}} = {{v.hash}}, // {{v.display}}
  {%- endfor %}
} Hv_{{name}}_EventOut;
{% endif -%}

{% if externs.tables|length > 0 %}
typedef enum {
  {%- for k,v in externs.tables %}
  HV_{{name|upper}}_TABLE_{{k|upper}} = {{v.hash}}, // {{v.display}}
  {%- endfor %}
} Hv_{{name}}_Table;
{%- endif %}

/**
 * Creates a new patch instance.
 * Sample rate should be positive and in Hertz, e.g. 44100.0.
 */
HeavyContextInterface *hv_{{name}}_new(double sampleRate);

/**
 * Creates a new patch instance.
 * @param sampleRate  Sample rate should be positive (> 0) and in Hertz, e.g. 48000.0.
 * @param poolKb  Pool size is in kilobytes, and determines the maximum amount of memory
 *   allocated to messages at any time. By default this is 10 KB.
 * @param inQueueKb  The size of the input message queue in kilobytes. It determines the
 *   amount of memory dedicated to holding scheduled messages between calls to
 *   process(). Default is 2 KB.
 * @param outQueueKb  The size of the output message queue in kilobytes. It determines the
 *   amount of memory dedicated to holding scheduled messages to the default sendHook.
 *   See getNextSentMessage() for info on accessing these messages. Default is 0 KB.
 */
HeavyContextInterface *hv_{{name}}_new_with_options(double sampleRate, int poolKb, int inQueueKb, int outQueueKb);

/**
 * Free the patch instance.
 */
void hv_{{name}}_free(HeavyContextInterface *instance);


#ifdef __cplusplus
} // extern "C"
#endif

#endif // _HEAVY_{{name|upper}}_H_
{# force a new line #}
