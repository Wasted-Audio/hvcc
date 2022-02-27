{{copyright}}

#ifndef __HeavyPatch_hpp__
#define __HeavyPatch_hpp__

#include "Patch.h"
#include "basicmaths.h"
#include "HvHeavy.h"
#include "Heavy_{{name}}.hpp"
#include "HeavyOwlConstants.h"

#define BUTTON_Push PUSHBUTTON
#define BUTTON_B1 BUTTON_A
#define BUTTON_B2 BUTTON_B
#define BUTTON_B3 BUTTON_C
#define BUTTON_B4 BUTTON_D
#define BUTTON_B5 BUTTON_E
#define BUTTON_B6 BUTTON_F
#define BUTTON_B7 BUTTON_G
#define BUTTON_B8 BUTTON_H

#define HV_HASH_NOTEIN          0x67E37CA3
#define HV_HASH_CTLIN           0x41BE0f9C
#define HV_HASH_PGMIN           0x2E1EA03D
#define HV_HASH_TOUCHIN         0x553925BD
#define HV_HASH_BENDIN          0x3083F0F7
#define HV_HASH_MIDIIN          0x149631bE
#define HV_HASH_MIDIREALTIMEIN  0x6FFF0BCF

#define HV_HASH_NOTEOUT         0xD1D4AC2
#define HV_HASH_CTLOUT          0xE5e2A040
#define HV_HASH_PGMOUT          0x8753E39E
#define HV_HASH_TOUCHOUT        0x476D4387
#define HV_HASH_BENDOUT         0xE8458013
#define HV_HASH_MIDIOUT         0x6511DE55
#define HV_HASH_MIDIOUTPORT     0x165707E4

#define HEAVY_MESSAGE_POOL_SIZE  4 // in kB (default 10kB)
#define HEAVY_MESSAGE_IN_QUEUE_SIZE 1 // in kB (default 2kB)
#define HEAVY_MESSAGE_OUT_QUEUE_SIZE 0 // in kB (default 0kB)

extern "C" {
  volatile bool _msgLock = false;
  static bool isButtonPressed(PatchButtonId bid){
    return getProgramVector()->buttons & (1<<bid);
  }
  static void setButton(PatchButtonId bid, bool pressed){
    if(pressed)
      getProgramVector()->buttons |= 1<<bid;
    else
      getProgramVector()->buttons &= ~(1<<bid);
  }
  static void owlPrintHook(HeavyContextInterface* ctxt,
			   const char *printLabel,
			   const char *msgString,
			   const HvMessage *m) {
    char buf[64];
    char* dst = buf;
    int len = strnlen(printLabel, 48);
    dst = stpncpy(dst, printLabel, len);
    dst = stpcpy(dst, " ");
    dst = stpncpy(dst, msgString, 63-len);
    debugMessage(buf);
  }
  static void owlSendHook(HeavyContextInterface* ctxt,
			  const char *receiverName,
			  uint32_t sendHash,
			  const HvMessage *m);
}

class HeavyPatch : public Patch {
public:
  HeavyPatch() {
    context = new Heavy_owl(getSampleRate(),
			    HEAVY_MESSAGE_POOL_SIZE,
			    HEAVY_MESSAGE_IN_QUEUE_SIZE,
			    HEAVY_MESSAGE_OUT_QUEUE_SIZE);
    context->setUserData(this);
    context->setPrintHook(&owlPrintHook);
    context->setSendHook(&owlSendHook);
    {% for param, name, typ, namehash, minvalue, maxvalue, defvalue, button in jdata if button == False %}
    // {{name}}
    registerParameter(PARAMETER_{{param}}, HV_NAME_CHANNEL_{{param}});
    setParameterValue(PARAMETER_{{param}}, HV_DEFAULT_CHANNEL_{{param}});
    {% endfor %}
  }

  ~HeavyPatch() {
    delete context;
  }

  uint16_t getButtonValue(PatchButtonId bid, const HvMessage *m){
    if(hv_msg_getNumElements(m) > 0 && hv_msg_isFloat(m, 0))
      return hv_msg_getFloat(m, 0) > 0.5 ? 4095 : 0;
    else
      return isButtonPressed(bid) ? 0 : 4095; // toggle
  }

  void sendCallback(uint32_t sendHash, const HvMessage *m){
    switch(sendHash){
    case HV_HASH_NOTEOUT:
      {
      uint8_t note = hv_msg_getFloat(m, 0);
      uint8_t velocity = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      // debugMessage("noteout", note, velocity, ch);
      sendMidi(MidiMessage::note(ch, note, velocity));
      }
      break;
    case HV_HASH_CTLOUT:
      {
      uint8_t value = hv_msg_getFloat(m, 0);
      uint8_t cc = hv_msg_getFloat(m, 1);
      uint8_t ch = hv_msg_getFloat(m, 2);
      // debugMessage("ctlout", value, cc, ch);
      sendMidi(MidiMessage::cc(ch, cc, value));
      }
      break;
    case HV_HASH_BENDOUT:
      {
      uint16_t value = hv_msg_getFloat(m, 0);
      uint8_t ch = hv_msg_getFloat(m, 1);
      // debugMessage("bendout", value, ch);
      sendMidi(MidiMessage::pb(ch, value));
      }
      break;
    case HV_HASH_TOUCHOUT:
      sendMidi(MidiMessage::cp((uint8_t)hv_msg_getFloat(m, 1), (uint8_t)hv_msg_getFloat(m, 0)));
      break;
    case HV_HASH_PGMOUT:
      sendMidi(MidiMessage::pc((uint8_t)hv_msg_getFloat(m, 1), (uint8_t)hv_msg_getFloat(m, 0)));
      break;
      {% for param, name, typ, namehash, minvalue, maxvalue, defvalue, button in jdata if typ == 'SEND'%}
      {% if button == True %}
    // Button {{name}}
    case HV_HASH_{{typ}}_CHANNEL_{{param}}:
      setButton(BUTTON_{{param}}, (hv_msg_getFloat(m, 0)-HV_MIN_CHANNEL_{{param}})/
		(HV_MAX_CHANNEL_{{param}}-HV_MIN_CHANNEL_{{param}}) > 0.5);
      {% else %}
    // Parameter {{name}}
    case HV_HASH_{{typ}}_CHANNEL_{{param}}:
      setParameterValue(PARAMETER_{{param}}, (hv_msg_getFloat(m, 0)-HV_MIN_CHANNEL_{{param}})/
  		        (HV_MAX_CHANNEL_{{param}}-HV_MIN_CHANNEL_{{param}}));
      {% endif %}
      break;
      {% endfor %}
    default:
      break;
    }
  }

  void processMidi(MidiMessage msg){
    // sendMessageToReceiverV parses format and loops over args, see HeavyContext.cpp
    switch(msg.getStatus()){
    case CONTROL_CHANGE:
      context->sendMessageToReceiverV
	(HV_HASH_CTLIN, 0, "fff",
	 (float)msg.getControllerValue(), // value
	 (float)msg.getControllerNumber(), // controller number
	 (float)msg.getChannel());
      break;
    case NOTE_ON:
      context->sendMessageToReceiverV
	(HV_HASH_NOTEIN, 0, "fff",
	 (float)msg.getNote(), // pitch
	 (float)msg.getVelocity(), // velocity
	 (float)msg.getChannel());
      break;
    case NOTE_OFF:
      context->sendMessageToReceiverV
	(HV_HASH_NOTEIN, 0, "fff",
	 (float)msg.getNote(), // pitch
	 0.0f, // velocity
	 (float)msg.getChannel());
      break;
    case CHANNEL_PRESSURE:
      context->sendMessageToReceiverV
	(HV_HASH_TOUCHIN, 0, "ff",
	 (float)msg.getChannelPressure(),
	 (float)msg.getChannel());
      break;
    case PITCH_BEND_CHANGE:
      context->sendMessageToReceiverV
	(HV_HASH_BENDIN, 0, "ff",
	 (float)msg.getPitchBend(),
	 (float)msg.getChannel());
      break;
    case PROGRAM_CHANGE:
      context->sendMessageToReceiverV
	(HV_HASH_PGMIN, 0, "ff",
	 (float)msg.getProgramChange(),
	 (float)msg.getChannel());
      break;
    default:
      break;
    }
  }

  void buttonChanged(PatchButtonId bid, uint16_t value, uint16_t samples){
    if(_msgLock)
      return;
    switch(bid){
    {% for param, name, typ, namehash, minvalue, maxvalue, defvalue, button in jdata if typ == 'RECV' and button == True %}
    // {{name}}
    case BUTTON_{{param}}:
      context->sendFloatToReceiver(HV_HASH_{{typ}}_CHANNEL_{{param}}, isButtonPressed(BUTTON_{{param}})*
				 (HV_MAX_CHANNEL_{{param}}-HV_MIN_CHANNEL_{{param}})+HV_MIN_CHANNEL_{{param}});
      break;
    {% endfor %}
    default:
      break;
    }
  }

  void processAudio(AudioBuffer &buffer) {
    _msgLock = true;
    {% for param, name, typ, namehash, minvalue, maxvalue, defvalue, button in jdata if typ == 'RECV' and button == False %}
    // {{name}}
      context->sendFloatToReceiver(HV_HASH_{{typ}}_CHANNEL_{{param}}, getParameterValue(PARAMETER_{{param}})*
				 (HV_MAX_CHANNEL_{{param}}-HV_MIN_CHANNEL_{{param}})+HV_MIN_CHANNEL_{{param}});
    {% endfor %}

    _msgLock = false;
    float* outputs[] = {buffer.getSamples(LEFT_CHANNEL), buffer.getSamples(RIGHT_CHANNEL)};
    context->process(outputs, outputs, getBlockSize());
  }

private:
  HeavyContext* context;
};

static void owlSendHook(HeavyContextInterface* ctxt,
			const char *receiverName,
			uint32_t sendHash,
			const HvMessage *m){
  HeavyPatch* patch = (HeavyPatch*)ctxt->getUserData();
  patch->sendCallback(sendHash, m);
}

#endif // __HeavyPatch_hpp__
