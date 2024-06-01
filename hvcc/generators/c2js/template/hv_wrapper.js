{{copyright}}

var audioWorkletSupported = (typeof AudioWorklet === 'function');

/*
 * AudioLibLoader - Convenience functions for setting up the web audio context
 * and initialising the AudioLib context
 */

var AudioLibLoader = function() {
  this.isPlaying = false;
  this.webAudioContext = null;
  this.webAudioProcessor = null;
  this.webAudioWorklet = null;
  this.audiolib = null;
}

/*
 * @param (Object) options
 *   @param options.blockSize (Number) number of samples to process in each iteration
 *   @param options.printHook (Function) callback that gets triggered on each print message
 *   @param options.sendHook (Function) callback that gets triggered for messages sent via @hv_param/@hv_event
 */
AudioLibLoader.prototype.init = function(options) {
  // use provided web audio context or create a new one
  this.webAudioContext = options.webAudioContext ||
      (new (window.AudioContext || window.webkitAudioContext || null));

  if (this.webAudioContext) {
    return (async() => {
      var blockSize = options.blockSize || 2048;
      if (audioWorkletSupported) {
        await this.webAudioContext.audioWorklet.addModule("{{name}}_AudioLibWorklet.js");
        this.webAudioWorklet = new AudioWorkletNode(this.webAudioContext, "{{name}}_AudioLibWorklet", {
          outputChannelCount: [2],
          processorOptions: {
            sampleRate: this.webAudioContext.sampleRate,
            blockSize,
          }
        });
        this.webAudioWorklet.port.onmessage = (event) => {
          if (event.data.type === 'printHook' && options.printHook) {
            options.printHook(event.data.payload);
          } else if (event.data.type === 'sendHook' && options.sendHook) {
            options.sendHook(event.data.payload[0], event.data.payload[1]);
          } else {
            console.log('Unhandled message from {{name}}_AudioLibWorklet:', event.data);
          }
        };
        this.webAudioWorklet.connect(this.webAudioContext.destination);
      } else {
        console.warn('heavy: AudioWorklet not supported, reverting to ScriptProcessorNode');
        var instance = new {{name}}_AudioLib({
            sampleRate: this.webAudioContext.sampleRate,
            blockSize: blockSize,
            printHook: options.printHook,
            sendHook: options.sendHook
        });
        this.audiolib = instance;
        this.webAudioProcessor = this.webAudioContext.createScriptProcessor(blockSize, instance.getNumInputChannels(), Math.max(instance.getNumOutputChannels(), 1));
        this.webAudioProcessor.onaudioprocess = (function(e) {
            instance.process(e)
        })
      }
    })();
  } else {
    console.error("heavy: failed to load - WebAudio API not available in this browser")
  }
}

AudioLibLoader.prototype.start = function() {
  if (this.audiolib) {
    this.webAudioProcessor.connect(this.webAudioContext.destination);
  } else {
    this.webAudioContext.resume();
  }
  this.isPlaying = true;
}

AudioLibLoader.prototype.stop = function() {
  if (this.audiolib) {
    this.webAudioProcessor.disconnect(this.webAudioContext.destination);
  } else {
    this.webAudioContext.suspend();
  }
  this.isPlaying = false;
}

AudioLibLoader.prototype.sendFloatParameterToWorklet = function(name, value) {
  this.webAudioWorklet.port.postMessage({
    type:'setFloatParameter',
    name,
    value
  });
}

AudioLibLoader.prototype.sendEvent = function(name, value) {
  this.webAudioWorklet.port.postMessage({
    type:'sendEvent',
    name,
    value
  });
}

AudioLibLoader.prototype.sendMidi = function(message) {
  this.webAudioWorklet.port.postMessage({
    type:'sendMidi',
    message:message
  });
}

AudioLibLoader.prototype.fillTableWithFloatBuffer = function(name, buffer) {
  this.webAudioWorklet.port.postMessage({
    type:'fillTableWithFloatBuffer',
    name,
    buffer
  });
}

Module.AudioLibLoader = AudioLibLoader;


/*
 * Heavy Javascript AudioLib - Wraps over the Heavy C API
 */

/*
 * @param (Object) options
 *   @param options.sampleRate (Number) audio sample rate
 *   @param options.blockSize (Number) number of samples to process in each iteration
 *   @param options.printHook (Function) callback that gets triggered on each print message
 *   @param options.sendHook (Function) callback that gets triggered for messages sent via @hv_param/@hv_event
 */
var {{name}}_AudioLib = function(options) {
  this.sampleRate = options.sampleRate || 44100.0;
  this.blockSize = options.blockSize || 2048;

  // instantiate heavy context
  this.heavyContext = _hv_{{name}}_new_with_options(this.sampleRate, {{pool_sizes_kb.internal}}, {{pool_sizes_kb.inputQueue}}, {{pool_sizes_kb.outputQueue}});
  this.setPrintHook(options.printHook);
  this.setSendHook(options.sendHook);

  // allocate temporary buffers (pointer size is 4 bytes in javascript)
  var lengthInSamples = this.blockSize * this.getNumOutputChannels();
  this.processBuffer = new Float32Array(
      Module.HEAPF32.buffer,
      Module._malloc(lengthInSamples * Float32Array.BYTES_PER_ELEMENT),
      lengthInSamples);
}

var parameterInHashes = {
  {%- for k,v in externs.parameters.in %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var parameterOutHashes = {
  {%- for k,v in externs.parameters.out %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var eventInHashes = {
  {%- for k,v in externs.events.in %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var eventOutHashes = {
  {%- for k,v in externs.events.out %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

var tableHashes = {
  {%- for k,v in externs.tables %}
  "{{v.display}}": {{v.hash}}, // {{v.display}}
  {%- endfor %}
};

{{name}}_AudioLib.prototype.process = function(event) {
    _hv_processInline(this.heavyContext, null, this.processBuffer.byteOffset, this.blockSize);

    for (var i = 0; i < this.getNumOutputChannels(); ++i) {
      var output = event.outputBuffer.getChannelData(i);

      var offset = i * this.blockSize;
      for (var j = 0; j < this.blockSize; ++j) {
        output[j] = this.processBuffer[offset+j];
      }
    }
}

{{name}}_AudioLib.prototype.getNumInputChannels = function() {
  return (this.heavyContext) ? _hv_getNumInputChannels(this.heavyContext) : -1;
}

{{name}}_AudioLib.prototype.getNumOutputChannels = function() {
  return (this.heavyContext) ? _hv_getNumOutputChannels(this.heavyContext) : -1;
}

{{name}}_AudioLib.prototype.setPrintHook = function(hook) {
  if (!this.heavyContext) {
    console.error("heavy: Can't set Print Hook, no Heavy Context instantiated");
    return;
  }

  if (hook) {
    // typedef void (HvPrintHook_t) (HeavyContextInterface *context, const char *printName, const char *str, const HvMessage *msg);
    var printHook = addFunction(function(context, printName, str, msg) {
        // Converts Heavy print callback to a printable message
        var timeInSecs =_hv_samplesToMilliseconds(context, _hv_msg_getTimestamp(msg)) / 1000.0;
        var m = UTF8ToString(printName) + " [" + timeInSecs.toFixed(3) + "]: " + UTF8ToString(str);
        hook(m);
      },
      "viiii"
    );
    _hv_setPrintHook(this.heavyContext, printHook);
  }
}

{{name}}_AudioLib.prototype.setSendHook = function(hook) {
  if (!this.heavyContext) {
      console.error("heavy: Can't set Send Hook, no Heavy Context instantiated");
      return;
  }

  if (hook) {
    // typedef void (HvSendHook_t) (HeavyContextInterface *context, const char *sendName, hv_uint32_t sendHash, const HvMessage *msg);
    var sendHook = addFunction(function(context, sendName, sendHash, msg) {
        // Converts sendhook callback to (sendName, float) message
        hook(UTF8ToString(sendName), _hv_msg_getFloat(msg, 0));
      },
      "viiii"
    );
    _hv_setSendHook(this.heavyContext, sendHook);
  }
}

{{name}}_AudioLib.prototype.sendEvent = function(name) {
  if (this.heavyContext) {
    _hv_sendBangToReceiver(this.heavyContext, eventInHashes[name]);
  }
}

{{name}}_AudioLib.prototype.sendMidi = function(message) {
  if (this.heavyContext) {
    var command = message[0] & 0xF0;
    var channel = message[0] & 0x0F;
    var data1 = message[1];
    var data2 = message[2];

    // all events to [midiin]
    for (var i = 1; i <= 2; i++) {
      _hv_sendMessageToReceiverFF(this.heavyContext, HV_HASH_MIDIIN, 0,
          message[i],
          channel
      );
    }

    // realtime events to [midirealtimein]
    if (MIDI_REALTIME.includes(message[0])) {
      _hv_sendMessageToReceiverFF(this.heavyContext, HV_HASH_MIDIREALTIMEIN, 0,
        message[0]
      );
    }

    switch(command) {
      case 0x80: // note off
        _hv_sendMessageToReceiverFFF(this.heavyContext, HV_HASH_NOTEIN, 0,
          data1,
          0,
          channel);
        break;
      case 0x90: // note on
        _hv_sendMessageToReceiverFFF(this.heavyContext, HV_HASH_NOTEIN, 0,
          data1,
          data2,
          channel);
        break;
      case 0xA0: // polyphonic aftertouch
        _hv_sendMessageToReceiverFFF(this.heavyContext, HV_HASH_POLYTOUCHIN, 0,
          data2, // pressure
          data1, // note
          channel);
        break;
      case 0xB0: // control change
        _hv_sendMessageToReceiverFFF(this.heavyContext, HV_HASH_CTLIN, 0,
          data2, // value
          data1, // cc number
          channel);
        break;
      case 0xC0: // program change
        _hv_sendMessageToReceiverFF(this.heavyContext, HV_HASH_PGMIN, 0,
          data1,
          channel);
        break;
      case 0xD0: // aftertouch
        _hv_sendMessageToReceiverFF(this.heavyContext, HV_HASH_TOUCHIN, 0,
          data1,
          channel);
        break;
      case 0xE0: // pitch bend
        // combine 7bit lsb and msb into 32bit int
        var value = (data2 << 7) | data1;
        _hv_sendMessageToReceiverFF(this.heavyContext, HV_HASH_BENDIN, 0,
          value,
          channel);
        break;
      default:
        // console.error('No handler for midi message: ', message);
    }
  }
}

{{name}}_AudioLib.prototype.setFloatParameter = function(name, floatValue) {
  if (this.heavyContext) {
    _hv_sendFloatToReceiver(this.heavyContext, parameterInHashes[name], parseFloat(floatValue));
  }
}

{{name}}_AudioLib.prototype.sendStringToReceiver = function(name, message) {
  // Note(joe): it's not a good idea to call this frequently it is possible for
  // the stack memory to run out over time.
  if (this.heavyContext) {
    var r = allocate(intArrayFromString(name), 'i8', ALLOC_STACK);
    var m = allocate(intArrayFromString(message), 'i8', ALLOC_STACK);
    _hv_sendSymbolToReceiver(this.heavyContext, _hv_stringToHash(r), m);
  }
}

{{name}}_AudioLib.prototype.fillTableWithFloatBuffer = function(name, buffer) {
  var tableHash = tableHashes[name];
  if (_hv_table_getBuffer(this.heavyContext, tableHash) !== 0) {

    // resize current table to new buffer length
    _hv_table_setLength(this.heavyContext, tableHash, buffer.length);

    // access internal float buffer from table
    tableBuffer = new Float32Array(
      Module.HEAPF32.buffer,
      _hv_table_getBuffer(this.heavyContext, tableHash),
      buffer.length);

    // set the table buffer with the data from the 1st channel (mono)
    tableBuffer.set(buffer);
  } else {
    console.error("heavy: Table '" + name + "' doesn't exist in the patch context.");
  }
}

Module.{{name}}_AudioLib = {{name}}_AudioLib;


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
