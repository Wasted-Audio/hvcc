{{copyright}}

#include "Heavy_{{patch_name}}.h"
#include "Heavy_{{patch_name}}.hpp" 
#include "HeavyDaisy_{{patch_name}}.hpp"                                                                 

#define SAMPLE_RATE 48000.f

using namespace daisy;

json2daisy::Daisy{{ class_name|capitalize }} hardware;

Heavy_{{patch_name}} hv(SAMPLE_RATE);

void audiocallback(daisy::AudioHandle::InputBuffer in, daisy::AudioHandle::OutputBuffer out, size_t size);
static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m);
void CallbackWriteIn(Heavy_{{patch_name}}& hv);
void LoopWriteIn(Heavy_{{patch_name}}& hv);
void CallbackWriteOut();
void LoopWriteOut();
void PostProcess();
void Display();

{% if  output_parameters|length > 0 %}
constexpr int DaisyNumOutputParameters = {{output_parameters|length}};
/** This array holds the output values received from PD hooks. These values are
 *  then written at the appropriate time in the following callback or loop.
 */
float output_data[DaisyNumOutputParameters];

struct DaisyHvParamOut
{
	uint32_t hash;
	uint32_t index;
  void (*hook_write_out)(float);

	void Process(float sig)
	{
		output_data[index] = sig;
    if (hook_write_out)
      (*hook_write_out)(sig);
	}
};

{% for param in hook_write_out %}
void {{param.name}}_hook(float sig) {
  {{param.process}}
};
{% endfor %}

DaisyHvParamOut DaisyOutputParameters[DaisyNumOutputParameters] = {
	{% for param in output_parameters %}
  {% if param.hook %}
    { (uint32_t) HV_{{patch_name|upper}}_PARAM_OUT_{{param.hash_enum|upper}}, {{param.index}}, &{{param.name}}_hook }, // {{param.name}}
  {% else %}
		{ (uint32_t) HV_{{patch_name|upper}}_PARAM_OUT_{{param.hash_enum|upper}}, {{param.index}}, nullptr }, // {{param.name}}
  {% endif %}
	{% endfor %}
};
{% endif %}

int main(void)
{
  hardware.Init(true);
  hardware.StartAudio(audiocallback);

  hv.setSendHook(sendHook);

  for(;;)
  {
    hardware.LoopProcess();
    Display();
    {% if loop_write_in|length > 0 %}
    LoopWriteIn(hv);
    {% endif %}
    {% if  output_parameters|length > 0 %}
    LoopWriteOut();
    {% endif %}
  }
}

/** The audio processing function. At the standard 48KHz sample rate and a block
 *  size of 48, this will fire every millisecond.
 */
void audiocallback(daisy::AudioHandle::InputBuffer in, daisy::AudioHandle::OutputBuffer out, size_t size)
{
  {% if num_output_channels == 0 %}
  // A zero fill to keep I/O quiet for a patch lacking ADC~/DAC~
  for (size_t chn = 0; chn < {{max_channels}}; chn++)
  {
    for (size_t i = 0; i < size; i++)
      out[chn][i] = 0;
  }
  {% endif %}
  {% if  parameters|length > 0 %}
  hardware.ProcessAllControls();
  CallbackWriteIn(hv);
  {% endif %}
  hv.process((float**)in, (float**)out, size);
  {% if  output_parameters|length > 0 %}
  CallbackWriteOut();
  {% endif %}
  hardware.PostProcess();
}

/** Receives messages from PD and writes them to the appropriate 
 *  index in the `output_data` array, to be written later.
 */
static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m) 
{
  {% if  output_parameters|length > 0 %}
  for (int i = 0; i < DaisyNumOutputParameters; i++)
  {
    if (DaisyOutputParameters[i].hash == receiverHash)
    {
      DaisyOutputParameters[i].Process(msg_getFloat(m, 0));
    }
  }
  {% endif %}
}

/** Sends signals from the Daisy hardware to the PD patch via the receive objects during the main loop
 * 
 */
void LoopWriteIn(Heavy_{{patch_name}}& hv)
{
  {% for param in loop_write_in %}
  {% if param.bool %} 
  if ({{param.process}})
    hv.sendBangToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}); 
  {% else %}
  hv.sendFloatToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}, {{param.process}}); 
  {% endif %}
  {% endfor %}
}

/** Sends signals from the Daisy hardware to the PD patch via the receive objects during the audio callback
 * 
 */
void CallbackWriteIn(Heavy_{{patch_name}}& hv)
{
  {% for param in callback_write_in %}
  {% if param.bool %} 
  if ({{param.process}})
    hv.sendBangToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}); 
  {% else %}
  hv.sendFloatToReceiver((uint32_t) HV_{{patch_name|upper}}_PARAM_IN_{{param.hash_enum|upper}}, {{param.process}}); 
  {% endif %}
  {% endfor %}
}

/** Writes the values sent to PD's receive objects to the Daisy hardware during the main loop
 * 
 */
void LoopWriteOut() {
  {% for param in loop_write_out %}
  {% if param.bool %} 
  if ({{param.value}})
    {{param.process}}
  {% else %}
  {{param.process}}
  {% endif %}
  {% endfor %}
}

/** Writes the values sent to PD's receive objects to the Daisy hardware during the audio callback
 * 
 */
void CallbackWriteOut() {
  {% for param in callback_write_out %}
  {% if param.bool %} 
  if ({{param.value}})
    {{param.process}}
  {% else %}
  {{param.process}}
  {% endif %}
  {% endfor %}
}

/** Handles the display code if the hardware defines a display
 * 
 */
void Display() {
  {{displayprocess}}
}
