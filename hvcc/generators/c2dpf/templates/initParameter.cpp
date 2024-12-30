      case param{{v.display}}:
        parameter.name = "{{v.display.replace('_', ' ')}}";
        parameter.symbol = "{{v.display|lower}}";
      {%- if v.attributes.type == 'db': %}
        parameter.unit = "dB";
      {%- elif v.attributes.type in ['hz', 'log_hz']: %}
        parameter.unit = "Hz";
      {%- endif %}
      {%- if v.type == "send" %}
        parameter.hints = kParameterIsOutput
      {%- else %}
        parameter.hints = kParameterIsAutomatable
      {%- endif %}
      {%- if v.attributes.type == 'bool': %}
        | kParameterIsBoolean
      {%- elif v.attributes.type == 'trig': -%}
        | kParameterIsTrigger
      {%- elif v.attributes.type == 'int': -%}
        | kParameterIsInteger
      {%- elif v.attributes.type in ['log', 'log_hz']: -%}
        | kParameterIsLogarithmic
      {%- endif %};
        parameter.ranges.min = {{v.attributes.min}}f;
        parameter.ranges.max = {{v.attributes.max}}f;
        parameter.ranges.def = {{v.attributes.default}}f;
      {%- if v.attributes.type == 'db' and not (meta.enumerators != None and meta.enumerators[v.display] is defined): %}
        {
          ParameterEnumerationValue* const enumValues = new ParameterEnumerationValue[1];
          enumValues[0].value = {{v.attributes.min}}f;
          enumValues[0].label = "-inf";
          parameter.enumValues.count = 1;
          parameter.enumValues.values = enumValues;
        }
      {%- endif %}
      {%- if meta.enumerators != None and meta.enumerators[v.display] is defined %}
        {% set enums = meta.enumerators[v.display] %}
        {% set enumlen = enums|length %}
        if (ParameterEnumerationValue *values = new ParameterEnumerationValue[{{enumlen}}])
        {
          parameter.enumValues.restrictedMode = true;
          {% for i in enums -%}
          values[{{loop.index - 1}}].value = {{loop.index - 1}}.0f;
          values[{{loop.index - 1}}].label = "{{i}}";
          {% endfor -%}
          parameter.enumValues.count = {{enumlen}};
          parameter.enumValues.values = values;
        }
      {%- endif %}
        break;
