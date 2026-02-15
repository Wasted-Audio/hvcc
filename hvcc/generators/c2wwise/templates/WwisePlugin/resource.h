{{copyright}}

#ifndef _HV_{{name|upper}}_WWISE_RESOURCE_H_
#define _HV_{{name|upper}}_WWISE_RESOURCE_H_

#define IDD_HV_{{name|upper}}_PLUGIN_SMALL   15
#define IDD_HV_{{name|upper}}_PLUGIN_BIG     16
#define IDC_STATIC_PARAMETER_IN_GROUP 4000
#define IDC_STATIC_PARAMETER_OUT_GROUP 5000
#define IDC_STATIC_TABLE_GROUP 6000

// Auto-generated Heavy parameters
{% for k, v in parameters %}
#define IDC_STATIC_HV_PARAM_{{k|upper}}    {{4000 + (loop.index*3)}}
#define IDC_RANGE_HV_PARAM_{{k|upper}}     {{4001 + (loop.index*3)}}
#define IDS_HV_PARAM_{{k|upper}}           {{4002 + (loop.index*3)}}
{%- endfor %}
{% for k, v in sends %}
#define IDC_STATIC_HV_PARAM_OUT_{{k|upper}}    {{5000 + (loop.index*3)}}
{%- endfor %}
{% for k, v in tables %}
#define IDC_STATIC_HV_TABLE_{{k|upper}}    {{6000 + (loop.index*2)}}
#define IDC_BUTTON_HV_TABLE_{{k|upper}}    {{6001 + (loop.index*2)}}
{%- endfor %}

// Next default values for new objects
#ifdef APSTUDIO_INVOKED
#ifndef APSTUDIO_READONLY_SYMBOLS
#define _APS_NEXT_RESOURCE_VALUE        4015
#define _APS_NEXT_COMMAND_VALUE         32771
#define _APS_NEXT_CONTROL_VALUE         4037
#define _APS_NEXT_SYMED_VALUE           4004
#endif
#endif

#endif // _HV_{{name|upper}}_WWISE_RESOURCE_H_
{# force new line #}
