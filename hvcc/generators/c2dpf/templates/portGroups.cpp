void {{class_name}}::initAudioPort(bool input, uint32_t index, AudioPort& port)
{
    Plugin::initAudioPort(input, index, port);

    if (input)
    {
      switch (index)
      {
{%- if port_groups.input|length %}
  {%- for group, gConfig in port_groups.input.items() %}
    {%- for port, value in gConfig.items() %}
      case {{value[0] if value[0] is number else value}}:
        port.name    = "Input {{port}} ({{group}})";
        port.symbol  = "in_{{port|lower}}_{{group|lower}}";
        port.groupId = kPortGroup{{group}};
      {%- if value[1] is sameas true %}
        port.hints   = kAudioPortIsCV | kCVPortHasPositiveUnipolarRange | kCVPortHasScaledRange | kCVPortIsOptional;
      {%- endif %}
        break;
    {%- endfor %}
  {%- endfor %}
{%- else %}
  {%- if num_input_channels == 2 %}
      case 0:
        port.name   = "Input Left";
        port.symbol = "in_left";
        break;
      case 1:
        port.name   = "Input Right";
        port.symbol = "in_right";
        break;
      port.groupId = kPortGroupStereo;
  {%- endif %}
{%- endif %}
      }
    }
    else
    {
      switch (index)
      {
{%- if port_groups.output|length %}
  {%- for group, gConfig in port_groups.output.items() %}
    {%- for port, value in gConfig.items() %}
      case {{value[0] if value[0] is number else value}}:
        port.name    = "Output {{port}} ({{group}})";
        port.symbol  = "out_{{port|lower}}_{{group|lower}}";
        port.groupId = kPortGroup{{group}};
      {%- if value[1] is sameas true %}
        port.hints   = kAudioPortIsCV | kCVPortHasPositiveUnipolarRange | kCVPortHasScaledRange | kCVPortIsOptional;
      {%- endif %}
        break;
    {%- endfor %}
  {%- endfor %}
{% else %}
  {%- if num_output_channels == 2 %}
      case 0:
        port.name   = "Output Left";
        port.symbol = "out_left";
        break;
      case 1:
        port.name   = "Output Right";
        port.symbol = "out_right";
        break;
      port.groupId = kPortGroupStereo;
  {%- endif %}
{%- endif %}
      }
    }
}


void {{class_name}}::initPortGroup(uint32_t groupId, PortGroup& portGroup)
{
  switch (groupId)
  {
{%- if port_groups.input|length or port_groups.output|length or port_groups.params|length%}
  {%- for group, value in (port_groups.input.items()|list) + (port_groups.output.items()|list) + (port_groups.params.items()|list) %}
    case kPortGroup{{group}}:
      portGroup.name   = "{{group}}";
      portGroup.symbol = "{{group|lower}}";
      break;
  {%- endfor %}
{%- endif %}
  }
}
