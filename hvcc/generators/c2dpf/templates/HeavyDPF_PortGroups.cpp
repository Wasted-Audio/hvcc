void {{class_name}}::initAudioPort(bool input, uint32_t index, AudioPort& port)
{
    port.hints = 0x0;

    if (input)
    {
      switch (index)
      {
{%- if meta.port_groups.input|length %}
  {%- for group, gConfig in meta.port_groups.input.items() %}
    {%- for port, value in gConfig.items() %}
      case {{value}}:
        port.name    = "Output {{port}} ({{group}})";
        port.symbol  = "out_{{port|lower}}_{{group|lower}}";
        port.groupId = kPortGroup{{group}};
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
{%- if meta.port_groups.output|length %}
  {%- for group, gConfig in meta.port_groups.output.items() %}
    {%- for port, value in gConfig.items() %}
      case {{value}}:
        port.name    = "Output {{port}} ({{group}})";
        port.symbol  = "out_{{port|lower}}_{{group|lower}}";
        port.groupId = kPortGroup{{group}};
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
      }
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
{%- if meta.port_groups.input|length %}
  {%- for group, value in meta.port_groups.input.items() %}
    case kPortGroup{{group}}:
      portGroup.name   = "{{group}}";
      portGroup.symbol = "{{group|lower}}";
      break;
  {%- endfor %}
{%- endif %}
{%- if meta.port_groups.output|length %}
  {%- for group, value in meta.port_groups.output.items() %}
    case kPortGroup{{group}}:
      portGroup.name   = "{{group}}";
      portGroup.symbol = "{{group|lower}}";
      break;
  {%- endfor %}
{%- endif %}
  }
}
