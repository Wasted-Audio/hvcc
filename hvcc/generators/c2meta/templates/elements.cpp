#include "CoreModules/CoreProcessor.hh"
#include "CoreModules/elements/element_counter.hh"
#include "CoreModules/elements/elements.hh"
#include "CoreModules/elements/element_info.hh"
#include "CoreModules/register_module.hh"
#include "HeavyMetaModule_{{name}}.hpp"


struct {{name}}MMInfo : MetaModule::ModuleInfoBase {
  static constexpr std::string_view slug{"{{ name }}"};
  static constexpr std::string_view description{"{{ meta.description }}"};
  static constexpr uint32_t width_hp = 10;
  static constexpr std::string_view png_filename{"{{ name }}/simple_gain.png"};

  {% raw %}
  static constexpr std::array<MetaModule::Element, 6> Elements{{
    MetaModule::Knob{{{{{20, 20, MetaModule::Coords::Center, "Vol"}, "tester/components/knob.png"}}, 0.5f}},
    MetaModule::JackInput{{{{10, 60, MetaModule::Coords::Center, "Input1"}, "tester/components/jack.png"}}},
    MetaModule::JackInput{{{{30, 60, MetaModule::Coords::Center, "Input2"}, "tester/components/jack.png"}}},
    MetaModule::JackOutput{{{{10, 80, MetaModule::Coords::Center, "Output1"}, "tester/components/jack.png"}}},
    MetaModule::JackOutput{{{{30, 80, MetaModule::Coords::Center, "Output2"}, "tester/components/jack.png"}}},
    MetaModule::MonoLight{{{{20, 35, MetaModule::Coords::Center, "Vol LED"}, "tester/components/led.png"}}}
  }};
  {% endraw %}
};

void init_{{ name|lower }}() {
  MetaModule::register_module<{{ name }}MM, {{name}}MMInfo>("{{ meta['brand'] }}");
}

// void init_{{ name|lower }}() {
//   // This is a simple way to create a ModuleInfoView
//   // See the README for better ways when dealing with more elements.

//   static std::array<MetaModule::Element, 6> elements;
//   static std::array<ElementCount::Indices, 6> indices;

//   MetaModule::Knob gain;
//   gain.x_mm = 20;
//   gain.y_mm = 20;
//   gain.image = "tester/components/knob.png";
//   gain.short_name = "Gain";
//   elements[0] = gain;
//   indices[0] = {.param_idx = VolID};

//   MetaModule::JackInput injack1;
//   injack1.x_mm = 10;
//   injack1.y_mm = 60;
//   injack1.image = "tester/components/jack.png";
//   injack1.short_name = "Input";
//   elements[1] = injack1;
//   indices[1] = {.input_idx = InputID0};

//   MetaModule::JackInput injack2;
//   injack2.x_mm = 30;
//   injack2.y_mm = 60;
//   injack2.image = "tester/components/jack.png";
//   injack2.short_name = "Input";
//   elements[2] = injack2;
//   indices[2] = {.input_idx = InputID1};

//   MetaModule::JackOutput outjack1;
//   outjack1.x_mm = 10;
//   outjack1.y_mm = 80;
//   outjack1.image = "tester/components/jack.png";
//   outjack1.short_name = "Output";
//   elements[3] = outjack1;
//   indices[3] = {.output_idx = OutputID0};

//   MetaModule::JackOutput outjack2;
//   outjack2.x_mm = 30;
//   outjack2.y_mm = 80;
//   outjack2.image = "tester/components/jack.png";
//   outjack2.short_name = "Output";
//   elements[4] = outjack2;
//   indices[4] = {.output_idx = OutputID1};

//   MetaModule::MonoLight light;
//   light.x_mm = 20;
//   light.y_mm = 35;
//   light.image = "tester/components/led.png";
//   light.short_name = "Gain LED";
//   elements[5] = light;
//   indices[5] = {.light_idx = LightID};

//   MetaModule::ModuleInfoView info{
//       .description = "{{ meta['description'] }}",
//       .width_hp = 10,
//       .elements = elements,
//       .indices = indices,
//   };

//   MetaModule::register_module<{{ name }}MM>("{{ name }}", "{{ name }}", info, "{{ name }}/simple_gain.png");
// }
