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
            printHook: options.printHook && options.printHook.toString(),
            sendHook: options.sendHook && options.sendHook.toString()
          }
        });
        this.webAudioWorklet.port.onmessage = (event) => {
          console.log('Message from {{name}}_AudioLibWorklet:', event.data);
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
  this.webAudioContext.resume();
  this.isPlaying = true;
}

AudioLibLoader.prototype.stop = function() {
  this.webAudioContext.suspend();
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
