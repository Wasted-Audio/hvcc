#include "CoreModules/CoreProcessor.hh"
#include "CoreModules/elements/element_counter.hh"
#include "CoreModules/elements/elements.hh"
#include "CoreModules/elements/element_info.hh"
#include "CoreModules/register_module.hh"
#include "HeavyMetaModule_{{name}}.hpp"

{%- set assets = meta.modules[0].assets %}
{%- set num_elements = assets.knobs|length + assets.leds|length + assets.inputs|length + assets.outputs|length %}
{%- set ns = namespace(counter=0) %}
{%- set ratio = 240/128.5 %}

void init_{{ name|lower }}() {
  static std::array<MetaModule::Element, {{num_elements}}> elements;
  static std::array<ElementCount::Indices, {{num_elements}}> indices;

{% for knob in assets.knobs %}
  MetaModule::Knob {{knob.param}};
  {{knob.param}}.x_mm = {{((knob.coords.x/ratio)|round(2))}};
  {{knob.param}}.y_mm = {{((knob.coords.y/ratio)|round(2))}};
  {{knob.param}}.coords = MetaModule::Coords::TopLeft;
  {{knob.param}}.image = "{{name}}/components/{{knob.image.name}}";
  {{knob.param}}.short_name = "{{knob.param}}";
  elements[{{ns.counter}}] = {{knob.param}};
  indices[{{ns.counter}}] = {.param_idx = {{knob.param|capitalize}}ID};
  {% set ns.counter = ns.counter + 1 %}
{%- endfor %}

{%- for input in assets.inputs %}
  MetaModule::JackInput injack{{input.id}};
  injack{{input.id}}.x_mm = {{((input.coords.x/ratio)|round(2))}};
  injack{{input.id}}.y_mm = {{((input.coords.y/ratio)|round(2))}};
  injack{{input.id}}.coords = MetaModule::Coords::TopLeft;
  injack{{input.id}}.image = "{{name}}/components/{{input.image.name}}";
  injack{{input.id}}.short_name = "Input {{input.id}}";
  elements[{{ns.counter}}] = injack{{input.id}};
  indices[{{ns.counter}}] = {.input_idx = InputID{{input.id}}};
  {% set ns.counter = ns.counter + 1 %}
{%- endfor %}

{%- for output in assets.outputs %}
  MetaModule::JackOutput outjack{{output.id}};
  outjack{{output.id}}.x_mm = {{((output.coords.x/ratio)|round(2))}};
  outjack{{output.id}}.y_mm = {{((output.coords.y/ratio)|round(2))}};
  outjack{{output.id}}.coords = MetaModule::Coords::TopLeft;
  outjack{{output.id}}.image = "{{name}}/components/{{output.image.name}}";
  outjack{{output.id}}.short_name = "Output {{output.id}}";
  elements[{{ns.counter}}] = outjack{{output.id}};
  indices[{{ns.counter}}] = {.output_idx = OutputID{{output.id}}};
  {% set ns.counter = ns.counter + 1 %}
{%- endfor %}

{%- for led in assets.leds %}
  MetaModule::MonoLight led{{led.led}};
  led{{led.led}}.x_mm = {{((led.coords.x/ratio)|round(2))}};
  led{{led.led}}.y_mm = {{((led.coords.y/ratio)|round(2))}};
  led{{led.led}}.coords = MetaModule::Coords::TopLeft;
  led{{led.led}}.image = "{{name}}/components/{{led.image.name}}";
  led{{led.led}}.short_name = "LED {{led.led}}";
  elements[{{ns.counter}}] = led{{led.led}};
  indices[{{ns.counter}}] = {.light_idx = {{led.led|capitalize}}ID};
  {% set ns.counter = ns.counter + 1 %}
{%- endfor %}

  MetaModule::ModuleInfoView info{
      .description = "{{ meta.description }}",
      .width_hp = {{ (assets.panel.size.x / 7.5) | round | int }},
      .elements = elements,
      .indices = indices,
  };

  MetaModule::register_module<{{ name }}MM>("{{ meta.name }}", "{{ meta.modules[0].name }}", info, "{{name}}/{{ assets.panel.image.name }}");
}
