{{copyright}}

#include "{{class_name}}.hpp"

#define SAMPLE_RATE 48000.f

using namespace daisy;

DSY_BOARD* hardware;

int num_params;

Heavy_{{name}} hv(SAMPLE_RATE);

void ProcessControls();

void audiocallback(float **in, float **out, size_t size)
{
    hv.process(in, out, size);
    ProcessControls();
}

static void sendHook(HeavyContextInterface *c, const char *receiverName, uint32_t receiverHash, const HvMessage * m) {
  // Do something with message sent from Pd patch through
  // [send receiverName @hv_event] object(s)
}

int main(void)
{
    hardware = &boardsHardware;
    {% if board == 'seed' %}
    hardware->Configure();
    {% endif %}
    num_params = hv.getParameterInfo(0,NULL);

    hv.setSendHook(sendHook);

    hardware->Init();

    {% if board != 'seed' %}
    hardware->StartAdc();
    {% endif %}

    hardware->StartAudio(audiocallback);
    // GENERATE POSTINIT
    for(;;)
    {
        {% if board == 'patch' %}
        hardware->DisplayControls(false);
        {% endif %}
    }
}

void ProcessControls()
{
    {% if board != 'seed' %}
    hardware->DebounceControls();
    hardware->UpdateAnalogControls();
    {% endif %}

    for (int i = 0; i < num_params; i++)
    {
	HvParameterInfo info;
	hv.getParameterInfo(i, &info);

    {% if board == 'seed' %}
    hv.sendFloatToReceiver(info.hash, 0.f);
    {% endif %}

	std::string name(info.name);

	for (int j = 0; j < DaisyNumParameters; j++){
	    if (DaisyParameters[j].name == name)
	    {
		float sig = DaisyParameters[j].Process();

		if (DaisyParameters[j].mode == ENCODER || DaisyParameters[j].mode == KNOB)
		    hv.sendFloatToReceiver(info.hash, sig);
		else if(sig)
		    hv.sendBangToReceiver(info.hash);
	    }
	}
    }
}
