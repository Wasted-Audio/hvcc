{{copyright}}

#ifndef _HEAVY_Daisy_{{name|upper}}_
#define _HEAVY_Daisy_{{name|upper}}_

#ifndef DSY_BOARDS_H
#define DSY_BOARDS_H
#ifndef DSY_BOARD
#define DSY_BOARD Daisy{{board.capitalize()}}
#endif
#endif

#include "Heavy_{{name}}.hpp"

#include "daisy_seed.h"
#include "daisy_pod.h"
#include "daisy_patch.h"
#include "daisy_field.h"
#include "daisy_petal.h"
#include <string>

using namespace daisy;

enum ControlType
{
    ENCODER,
    SWITCH,
    KNOB,
    GATE,
};


//All the info we need for our parameters
struct DaisyHvParam{

    std::string name;
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

	    case SWITCH:
	    {
		Switch* sw = static_cast<Switch*>(control);
		return sw->RisingEdge();
	    }

	    case KNOB:
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

DSY_BOARD boardsHardware;
    {% if board == 'seed' %}
int DaisyNumParameters = 0;
DaisyHvParam DaisyParameters[0];
    {% elif board == 'pod' %}
int DaisyNumParameters = 6;
DaisyHvParam DaisyParameters[6] = {
    {"Encoder",   &boardsHardware.encoder, ENCODER},
    {"EncSwitch", &boardsHardware.encoder, SWITCH},
    {"Knob1",     &boardsHardware.knob1,   KNOB},
    {"Knob2",     &boardsHardware.knob2,   KNOB},
    {"Button1",   &boardsHardware.button1, SWITCH},
    {"Button2",   &boardsHardware.button2, SWITCH},
};
    {% elif board == 'patch' %}
int DaisyNumParameters = 8;
DaisyHvParam DaisyParameters[8] = {
    {"Encoder",   &boardsHardware.encoder,       ENCODER},
    {"EncSwitch", &boardsHardware.encoder,       SWITCH},
    {"Ctrl1",     &boardsHardware.controls[0],   KNOB},
    {"Ctrl2",     &boardsHardware.controls[1],   KNOB},
    {"Ctrl3",     &boardsHardware.controls[2],   KNOB},
    {"Ctrl4",     &boardsHardware.controls[3],   KNOB},
    {"Gate1",     &boardsHardware.gate_input[0], GATE},
    {"Gate2",     &boardsHardware.gate_input[1], GATE},
};
    {% elif board == 'petal' %}
int DaisyNumParameters = 15;
DaisyHvParam DaisyParameters[15] = {
    {"Encoder",   &boardsHardware.encoder,     ENCODER},
    {"EncSwitch", &boardsHardware.encoder,     SWITCH},
    {"Knob1",     &boardsHardware.knob[0],     KNOB},
    {"Knob2",     &boardsHardware.knob[1],     KNOB},
    {"Knob3",     &boardsHardware.knob[2],     KNOB},
    {"Knob4",     &boardsHardware.knob[3],     KNOB},
    {"Knob5",     &boardsHardware.knob[4],     KNOB},
    {"Knob6",     &boardsHardware.knob[5],     KNOB},
    {"Switch1",   &boardsHardware.switches[0], SWITCH},
    {"Switch2",   &boardsHardware.switches[1], SWITCH},
    {"Switch3",   &boardsHardware.switches[2], SWITCH},
    {"Switch4",   &boardsHardware.switches[3], SWITCH},
    {"Switch5",   &boardsHardware.switches[4], SWITCH},
    {"Switch6",   &boardsHardware.switches[5], SWITCH},
    {"Switch7",   &boardsHardware.switches[6], SWITCH},
};
    {% endif %}


#endif // _HEAVY_Daisy2_{{name|upper}}_
