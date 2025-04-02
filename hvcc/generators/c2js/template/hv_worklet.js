{{copyright}}

/*
 * AudioLibWorklet - Processes the audio through the Heavy C API
 */

class {{name}}_AudioLibWorklet extends AudioWorkletProcessor {
    constructor({ processorOptions }) {
        super();
        this.sampleRate = processorOptions.sampleRate || 44100.0;

        // As of right now (June 2022), blockSize is always 128.
        // In the future, it could become dynamic,
        // and we'll have to read the lengths of incoming outputs and re-alloc the processBuffer if it changes.
        this.blockSize = 128;

        // instantiate heavy context
        this.heavyContext = _hv_{{name}}_new_with_options(this.sampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});

        this.setPrintHook();
        this.setSendHook();

        // allocate temporary buffers (pointer size is 4 bytes in javascript)
        var lengthInSamples = this.blockSize * this.getNumOutputChannels();
        this.processBuffer = new Float32Array(
            Module.HEAPF32.buffer,
            Module._malloc(lengthInSamples * Float32Array.BYTES_PER_ELEMENT),
            lengthInSamples);

        this.port.onmessage = (e) => {
          console.log(e.data);
          switch(e.data.type){
            case 'setFloatParameter':
              this.setFloatParameter(e.data.name, e.data.value);
              break;
            case 'sendEvent':
              this.sendEvent(e.data.name);
              break;
            case 'sendMidi':
              this.sendMidi(e.data.message);
              break;
            case 'fillTableWithFloatBuffer':
              this.fillTableWithFloatBuffer(e.data.name, e.data.buffer);
              break;
            default:
              console.error('No handler for message of type: ', e.data.type);
          }
        }
    }

    process(inputs, outputs, parameters) {
      try{
        _hv_processInline(this.heavyContext, null, this.processBuffer.byteOffset, this.blockSize);

        // TODO: Figure out what "multiple outputs" means if not multiple channels
        var output = outputs[0];

        for (var i = 0; i < this.getNumOutputChannels(); ++i) {
          var channel = output[i];

          var offset = i * this.blockSize;
          for (var j = 0; j < this.blockSize; ++j) {
            channel[j] = this.processBuffer[offset+j];
          }
        }
      } catch(e){
        this.port.postMessage({ type:'error', error: e.toString() });
      }
      return true;
    }

    getNumInputChannels() {
      return (this.heavyContext) ? _hv_getNumInputChannels(this.heavyContext) : -1;
    }

    getNumOutputChannels() {
      return (this.heavyContext) ? _hv_getNumOutputChannels(this.heavyContext) : -1;
    }

    setPrintHook() {
      if (!this.heavyContext) {
        console.error("heavy: Can't set Print Hook, no Heavy Context instantiated");
        return;
      }

      var self = this;
      // typedef void (HvPrintHook_t) (HeavyContextInterface *context, const char *printName, const char *str, const HvMessage *msg);
      var printHook = addFunction(function(context, printName, str, msg) {
          // Converts Heavy print callback to a printable message
          var timeInSecs =_hv_samplesToMilliseconds(context, _hv_msg_getTimestamp(msg)) / 1000.0;
          var m = UTF8ToString(printName) + " [" + timeInSecs.toFixed(3) + "]: " + UTF8ToString(str);
          self.port.postMessage({
            type: 'printHook',
            payload: m
          });
        },
        "viiii"
      );
      _hv_setPrintHook(this.heavyContext, printHook);
    }

    setSendHook() {
      if (!this.heavyContext) {
          console.error("heavy: Can't set Send Hook, no Heavy Context instantiated");
          return;
      }

      var self = this;
      // typedef void (HvSendHook_t) (HeavyContextInterface *context, const char *sendName, hv_uint32_t sendHash, const HvMessage *msg);
      var sendHook = addFunction(function(context, sendName, sendHash, msg) {
        // Filter out MIDI messages
        const midiMessage = sendMidiOut(UTF8ToString(sendName), msg);
        if (midiMessage.length > 0) {
          self.port.postMessage({
            type: 'midiOut',
            payload: midiMessage
          });
        } else {
          // Converts sendhook callback to (sendName, float) message
          self.port.postMessage({
            type: 'sendHook',
            payload: [UTF8ToString(sendName), _hv_msg_getFloat(msg, 0)]
          });
        }
      },
      "viiii"
      );
      _hv_setSendHook(this.heavyContext, sendHook);
    }

    sendEvent(name) {
      if (this.heavyContext) {
        _hv_sendBangToReceiver(this.heavyContext, eventInHashes[name]);
      }
    }

    setFloatParameter(name, floatValue) {
      if (this.heavyContext) {
        _hv_sendFloatToReceiver(this.heavyContext, parameterInHashes[name], parseFloat(floatValue));
      }
    }

    sendMidi(message) {
      sendMidiIn(this.heavyContext, message);
    }

    sendStringToReceiver(name, message) {
      // Note(joe): it's not a good idea to call this frequently it is possible for
      // the stack memory to run out over time.
      if (this.heavyContext) {
        var r = allocate(intArrayFromString(name), 'i8', ALLOC_STACK);
        var m = allocate(intArrayFromString(message), 'i8', ALLOC_STACK);
        _hv_sendSymbolToReceiver(this.heavyContext, _hv_stringToHash(r), m);
      }
    }

    fillTableWithFloatBuffer(name, buffer) {
      var tableHash = tableHashes[name];
      if (_hv_table_getBuffer(this.heavyContext, tableHash) !== 0) {

        // resize current table to new buffer length
        _hv_table_setLength(this.heavyContext, tableHash, buffer.length);

        // access internal float buffer from table
        let tableBuffer = new Float32Array(
          Module.HEAPF32.buffer,
          _hv_table_getBuffer(this.heavyContext, tableHash),
          buffer.length);

        // set the table buffer with the data from the 1st channel (mono)
        tableBuffer.set(buffer);
      } else {
        console.error("heavy: Table '" + name + "' doesn't exist in the patch context.");
      }
    }
}

var parameterInHashes = {
  {%- for k,v in externs.parameters.inParam %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var parameterOutHashes = {
  {%- for k,v in externs.parameters.outParam %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var eventInHashes = {
  {%- for k,v in externs.events.inEvent %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var eventOutHashes = {
  {%- for k,v in externs.events.outEvent %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var tableHashes = {
  {%- for k,v in externs.tables %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

registerProcessor("{{name}}_AudioLibWorklet", {{name}}_AudioLibWorklet);


// midi_utils

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

function sendMidiOut(sendName, msg) {
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
            var channel = _hv_msg_getFloat(msg, 2) % 16; // no pd midi ports
            return[
              160 | channel,
              note,
              value
            ]
          case "__hv_bendout":
            var value = _hv_msg_getFloat(msg, 0);
            let lsb = value & 0x7F;
            let msb = (value >> 7) & 0x7F;
            var channel = _hv_msg_getFloat(msg, 1) % 16; // no pd midi ports
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
