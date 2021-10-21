{{copyright}}

#include "{{class_name}}.hpp"

#define SAMPLE_RATE 48000.f

using namespace daisy;

Daisy hardware;
int num_params;

Heavy_{{name}} hv(SAMPLE_RATE);

void ProcessControls();

void audiocallback(daisy::AudioHandle::InterleavingInputBuffer in, daisy::AudioHandle::InterleavingOutputBuffer out, size_t size)
{
  hv.process((float**)in, (float**)out, size);
  ProcessControls();
  hardware.PostProcess();
}

static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m) 
{
  // Do something with message sent from Pd patch through
  // [send receiverName @hv_event] object(s)
}

int main(void)
{
  hardware.Init(true);
  hardware.driver.StartAudio(audiocallback);

  num_params = hv.getParameterInfo(0,NULL);
  hv.setSendHook(sendHook);

  // GENERATE POSTINIT
  for(;;)
  {
    hardware.Display();
  }
}

void ProcessControls()
{
  hardware.ProcessAllControls();

  for (int i = 0; i < num_params; i++)
  {
    HvParameterInfo info;
    hv.getParameterInfo(i, &info);

    if (DaisyNumParameters == 0)
      hv.sendFloatToReceiver(info.hash, 0.f);

    for (int j = 0; j < DaisyNumParameters; j++)
    {
      if (DaisyParameters[j].hash == info.hash)
      {
        float sig = DaisyParameters[j].Process();

        if (DaisyParameters[j].mode == ENCODER || DaisyParameters[j].mode == ANALOGCONTROL)
          hv.sendFloatToReceiver(info.hash, sig);
        else if(sig)
          hv.sendBangToReceiver(info.hash);
      }
    }
  }
}

DaisyHvParam DaisyParameters[DaisyNumParameters] = {
	{% for param in parameters %}
		{ {{param.hash}}, &hardware.{{param.name}}, {{param.type}} },
	{% endfor %}
};