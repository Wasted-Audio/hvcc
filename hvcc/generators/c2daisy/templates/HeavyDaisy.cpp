{{copyright}}

#include "{{class_name}}.hpp"

#define SAMPLE_RATE 48000.f

using namespace daisy;

Daisy hardware;

Heavy_{{name}} hv(SAMPLE_RATE);

void ProcessControls();

void audiocallback(daisy::AudioHandle::InputBuffer in, daisy::AudioHandle::OutputBuffer out, size_t size)
{
  hv.process((float**)in, (float**)out, size);
  {% if  parameters|length > 0 %}
  ProcessControls();
  {% endif %}
  {% if  output_parameters|length > 0 %}
  hardware.CallbackWriteOut();
  {% endif %}
  hardware.PostProcess();
}

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

int main(void)
{
  hardware.Init(true);
  hardware.driver.StartAudio(audiocallback);

  hv.setSendHook(sendHook);

  for(;;)
  {
    hardware.Display();
    {% if  output_parameters|length > 0 %}
    hardware.LoopWriteOut();
    {% endif %}
  }
}

void ProcessControls()
{
  hardware.ProcessAllControls();
  hardware.CallbackWriteIn(hv);
}

{% if  output_parameters|length > 0 %}
DaisyHvParamOut DaisyOutputParameters[DaisyNumOutputParameters] = {
	{% for param in output_parameters %}
		{ {{param.hash}}, {{param.index}} }, // {{param.name}}
	{% endfor %}
};
{% endif %}