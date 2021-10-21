{{copyright}}
#ifndef _HEAVY_DAISY_{{name|upper}}_
#define _HEAVY_DAISY_{{name|upper}}_

// #include <string>

#include "Heavy_{{name}}.hpp"

#define ANALOG_COUNT {{analogcount}}

{% if driver == 'seed' %}
#include "daisy_seed.h"
{% else %}
#include "daisy_patch_sm.h"
{% endif %}
{{display_conditional}}
// name: {{target_name}}
struct Daisy {
	void Init(bool boost = false) {

		{% if driver == 'seed' %}
		driver.Configure();
 		driver.Init(boost);
		{% else %}
		driver.Init();
		{% endif %}
        
		{{init}}
        
		{{switch}}
        
		{{switch3}}
        
		{{gatein}}
		
		{{encoder}}
		
		{{init_single}}
		
		{% if driver == 'seed' %}
		driver.adc.Init(cfg, ANALOG_COUNT);
		{% endif %}

		{{ctrl_init}}
		
		{{led}}
		
		{{rgbled}}
		
		{{gateout}}
		
		{{dachandle}}
		
		{{display}}
	}

	void ProcessAllControls() {
		{{process}}
	}

	void PostProcess() {
		{{postprocess}}
	}

	void Display() {
		{{displayprocess}}
	}

	void SetAudioSampleRate(daisy::SaiHandle::Config::SampleRate samplerate) {
		driver.SetAudioSampleRate(samplerate);
		SetHidUpdateRates();
	}
	void SetAudioBlockSize(size_t size) {
		driver.SetAudioBlockSize(size);
		SetHidUpdateRates();
	}

	void SetHidUpdateRates() {
		{{hidupdaterates}}
	}

	{% if driver == 'seed' %}
	daisy::DaisySeed driver;
	daisy::AdcChannelConfig cfg[ANALOG_COUNT];
	{% else %}
	daisy::patch_sm::PatchSM driver;
	{% endif %}
	
	{{comps}}
	
	{{dispdec}}
	
	int menu_click = 0, menu_hold = 0, menu_rotate = 0;

};

using namespace daisy;

enum ControlType
{
	ENCODER,
	ENCODER_PRESS,
	SWITCH,
	ANALOGCONTROL,
	GATE,
};

//All the info we need for our parameters
struct DaisyHvParam
{
	// std::string name;
	uint32_t hash;
	void* control;
	ControlType mode;

	float Process()
	{
		if (control == nullptr)
			return 0.f;

		switch (mode)
		{
			case ENCODER:
			{
				Encoder* enc = static_cast<Encoder*>(control);
				return enc->Increment();
			}
			case ENCODER_PRESS:
			{
				Encoder* enc = static_cast<Encoder*>(control);
				return enc->Pressed();
			}
			case SWITCH:
			{
				Switch* sw = static_cast<Switch*>(control);
				return sw->RisingEdge();
			}
			case ANALOGCONTROL:
			{
				AnalogControl* knob = static_cast<AnalogControl*>(control);
				return knob->Process();
			}
			case GATE:
			{
				GateIn* gate = static_cast<GateIn*>(control);
				return gate->Trig();
			}
		}

		return 0.f;
	}
};

constexpr int DaisyNumParameters = {{parameters|length}};
extern Daisy hardware;
extern DaisyHvParam DaisyParameters[DaisyNumParameters];

#endif // _HEAVY_DAISY_{{name|upper}}_