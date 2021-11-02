{{copyright}}
#ifndef _HEAVY_DAISY_{{name|upper}}_
#define _HEAVY_DAISY_{{name|upper}}_

// #include <string>

#include "Heavy_{{name}}.hpp"

#define ANALOG_COUNT {{analogcount}}

{% if driver == 'seed' %}
#include "daisy_seed.h"
#include "dev/codec_ak4556.h"
{% else %}
#include "daisy_patch_sm.h"
{% endif %}

using namespace daisy;

{{non_class_declarations}}

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

		{{i2c}}

		{{pca9685}}
        
		{{switch}}
        
		{{switch3}}

		{{cd4021}}
        
		{{gatein}}
		
		{{encoder}}
		
		{{init_single}}
		
		{% if driver == 'seed' %}
		driver.adc.Init(cfg, ANALOG_COUNT);
		{% endif %}

		{{ctrl_init}}

		{{ctrl_mux_init}}
		
		{{led}}
		
		{{rgbled}}
		
		{{gateout}}
		
		{{dachandle}}
		
		{{display}}


		{% if driver == 'seed' and external_codecs|length > 0 %}

		SaiHandle::Config sai_config[{{ 1 + external_codecs|length }}];

		// Internal Codec
    sai_config[0].periph          = SaiHandle::Config::Peripheral::SAI_1;
    sai_config[0].sr              = SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[0].bit_depth       = SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[0].a_sync          = SaiHandle::Config::Sync::MASTER;
    sai_config[0].b_sync          = SaiHandle::Config::Sync::SLAVE;
    sai_config[0].a_dir           = SaiHandle::Config::Direction::TRANSMIT;
    sai_config[0].b_dir           = SaiHandle::Config::Direction::RECEIVE;
    sai_config[0].pin_config.fs   = {DSY_GPIOE, 4};
    sai_config[0].pin_config.mclk = {DSY_GPIOE, 2};
    sai_config[0].pin_config.sck  = {DSY_GPIOE, 5};
    sai_config[0].pin_config.sa   = {DSY_GPIOE, 6};
    sai_config[0].pin_config.sb   = {DSY_GPIOE, 3};

		{% for codec in external_codecs %}
		sai_config[{{loop.index}}].periph          = SaiHandle::Config::Peripheral::{{codec.periph}};
    sai_config[{{loop.index}}].sr              = SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[{{loop.index}}].bit_depth       = SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[{{loop.index}}].a_sync          = SaiHandle::Config::Sync::{{codec.a_sync}};
    sai_config[{{loop.index}}].b_sync          = SaiHandle::Config::Sync::{{codec.b_sync}};
    sai_config[{{loop.index}}].a_dir           = SaiHandle::Config::Direction::{{codec.a_dir}};
    sai_config[{{loop.index}}].b_dir           = SaiHandle::Config::Direction::{{codec.b_dir}};
    sai_config[{{loop.index}}].pin_config.fs   = driver.GetPin({{codec.pin.fs}});
    sai_config[{{loop.index}}].pin_config.mclk = driver.GetPin({{codec.pin.mclk}});
    sai_config[{{loop.index}}].pin_config.sck  = driver.GetPin({{codec.pin.sck}});
    sai_config[{{loop.index}}].pin_config.sa   = driver.GetPin({{codec.pin.sa}});
    sai_config[{{loop.index}}].pin_config.sb   = driver.GetPin({{codec.pin.sb}});
		{% endfor %}

		SaiHandle sai_handle[{{ 1 + external_codecs|length }}];
		sai_handle[0].Init(sai_config[0]);
		{% for codec in external_codecs %}
		sai_handle[{{loop.index}}].Init(sai_config[{{loop.index}}]);
		{% endfor %}

		dsy_gpio_pin codec_reset_pin = driver.GetPin(29);
    Ak4556::Init(codec_reset_pin);

		AudioHandle::Config cfg;
    cfg.blocksize  = 48;
    cfg.samplerate = SaiHandle::Config::SampleRate::SAI_48KHZ;
    cfg.postgain   = 0.5f;
    driver.audio_handle.Init(
			cfg, 
			sai_handle[0]
			{% for codec in external_codecs %}
			,sai_handle[{{loop.index}}]
			{% endfor %}
		);

		{% endif %}

		{% if driver == 'seed' %}
		driver.adc.Start();
		{% endif %}

	}

	void ProcessAllControls() {
		{{process}}
		{% if driver == 'patch_sm' %}
		driver.ProcessAllControls();
		{% endif %}
	}

	void PostProcess() {
		{{postprocess}}
	}

	void Display() {
		{{displayprocess}}
	}

	void LoopWriteOut() {
		{{loop_write_out}}
	}

	void CallbackWriteOut() {
		{{callback_write_out}}
	}

	void CallbackWriteIn(Heavy_{{name}}& hv) {
		{% for param in callback_write_in %}
		{% if param.bool %} 
		if ({{param.process}})
			hv.sendBangToReceiver({{param.hash}}); 
		{% else %}
		hv.sendFloatToReceiver({{param.hash}}, {{param.process}}); 
		{% endif %}
		{% endfor %}
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
	daisy::patch_sm::DaisyPatchSM driver;
	{% endif %}
	
	{{comps}}
	{% if  output_parameters|length > 0 %}
	float output_data[{{output_parameters|length}}];
	{% endif %}
	
	{{dispdec}}
	
	int menu_click = 0, menu_hold = 0, menu_rotate = 0;

};

extern Daisy hardware;

{% if  output_parameters|length > 0 %}
struct DaisyHvParamOut
{
	uint32_t hash;
	uint32_t index;

	void Process(float sig)
	{
		hardware.output_data[index] = sig;
	}

};

constexpr int DaisyNumOutputParameters = {{output_parameters|length}};
extern DaisyHvParamOut DaisyOutputParameters[DaisyNumOutputParameters];
{% endif %}

#endif // _HEAVY_DAISY_{{name|upper}}_