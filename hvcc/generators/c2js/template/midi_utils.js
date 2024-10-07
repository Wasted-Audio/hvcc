// midi_utils.js

function sendMidiIn(hv_context, message) {
    if (hv_context) {
        var command = message[0] & 0xF0;
        var channel = message[0] & 0x0F;
        var data1 = message[1];
        var data2 = message[2];
    
        // all events to [midiin]
        for (var i = 1; i <= 2; i++) {
          _hv_sendMessageToReceiverFF(hv_context, HV_HASH_MIDIIN, 0,
              message[i],
              channel
          );
        }
    
        // realtime events to [midirealtimein]
        if (MIDI_REALTIME.includes(message[0])) {
          _hv_sendMessageToReceiverFF(hv_context, HV_HASH_MIDIREALTIMEIN, 0,
            message[0]
          );
        }
    
        switch(command) {
          case 0x80: // note off
            _hv_sendMessageToReceiverFFF(hv_context, HV_HASH_NOTEIN, 0,
              data1,
              0,
              channel);
            break;
          case 0x90: // note on
            _hv_sendMessageToReceiverFFF(hv_context, HV_HASH_NOTEIN, 0,
              data1,
              data2,
              channel);
            break;
          case 0xA0: // polyphonic aftertouch
            _hv_sendMessageToReceiverFFF(hv_context, HV_HASH_POLYTOUCHIN, 0,
              data2, // pressure
              data1, // note
              channel);
            break;
          case 0xB0: // control change
            _hv_sendMessageToReceiverFFF(hv_context, HV_HASH_CTLIN, 0,
              data2, // value
              data1, // cc number
              channel);
            break;
          case 0xC0: // program change
            _hv_sendMessageToReceiverFF(hv_context, HV_HASH_PGMIN, 0,
              data1,
              channel);
            break;
          case 0xD0: // aftertouch
            _hv_sendMessageToReceiverFF(hv_context, HV_HASH_TOUCHIN, 0,
              data1,
              channel);
            break;
          case 0xE0: // pitch bend
            // combine 7bit lsb and msb into 32bit int
            var value = (data2 << 7) | data1;
            _hv_sendMessageToReceiverFF(hv_context, HV_HASH_BENDIN, 0,
              value,
              channel);
            break;
          default:
            // console.error('No handler for midi message: ', message);
        }
      }
    }

function midiOutMsg(sendName, msg) {
    switch (sendName) {
            case "__hv_noteout":
              var note = _hv_msg_getFloat(msg, 0);
              var velocity = _hv_msg_getFloat(msg, 1);
              var channel = _hv_msg_getFloat(msg, 2) % 16; // no pd midi ports
              return [
                ((velocity > 0) ? 144 : 128) | channel,
                note,
                velocity
              ]
            case "__hv_ctlout":
              var value = _hv_msg_getFloat(msg, 0);
              var cc = _hv_msg_getFloat(msg, 1);
              var channel = _hv_msg_getFloat(msg, 2) % 16; // no pd midi ports
              return [
                176 | channel,
                cc,
                value
              ]
            case "__hv_pgmout":
              var program = _hv_msg_getFloat(msg, 0);
              var channel = _hv_msg_getFloat(msg, 1) % 16; // no pd midi ports
              return [
                192 | channel,
                program
              ]
            case "__hv_touchout":
              var pressure = _hv_msg_getFloat(msg, 0);
              var channel = _hv_msg_getFloat(msg, 1) % 16; // no pd midi ports
              return [
                208 | channel,
                pressure,
              ]
            case "__hv_polytouchout":
              var value = _hv_msg_getFloat(msg, 0);
              var note = _hv_msg_getFloat(msg, 1);
              var channel = _hv_msg_getFloat(msg, 2) % 16; // no pd midiports
              return[
                160 | channel,
                note,
                value
              ]
            case "__hv_bendout":
              var value = _hv_msg_getFloat(msg, 0);
              let lsb = value & 0x7F;
              let msb = (value >> 7) & 0x7F;
              var channel = _hv_msg_getFloat(msg, 2) % 16; // no pd midi ports
              return [
                224 | channel,
                lsb,
                msb
              ]
            case "__hv_midiout":
              let firstByte = _hv_msg_getFloat(msg, 0);
              return (firstByte === 192 || firstByte === 208) ? 
                [_hv_msg_getFloat(msg, 0), _hv_msg_getFloat(msg, 1)] :
                [_hv_msg_getFloat(msg, 0), _hv_msg_getFloat(msg, 1), _hv_msg_getFloat(msg, 2)];
            default:
                console.warn(`Unhandled sendName: ${sendName}`);
                return [];
    }
}

/*
 * MIDI Constants
 */

const HV_HASH_NOTEIN          = 0x67E37CA3;
const HV_HASH_CTLIN           = 0x41BE0f9C;
const HV_HASH_POLYTOUCHIN     = 0xBC530F59;
const HV_HASH_PGMIN           = 0x2E1EA03D;
const HV_HASH_TOUCHIN         = 0x553925BD;
const HV_HASH_BENDIN          = 0x3083F0F7;
const HV_HASH_MIDIIN          = 0x149631bE;
const HV_HASH_MIDIREALTIMEIN  = 0x6FFF0BCF;

const MIDI_REALTIME =  [0xF8, 0xFA, 0xFB, 0xFC, 0xFE, 0xFF];
