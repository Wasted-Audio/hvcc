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

        if (processorOptions.printHook) {
          this.setPrintHook(new Function(processorOptions.printHook));
        }

        if(processorOptions.sendHook) {
          this.setSendHook(new Function(processorOptions.sendHook));
        }

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

    setPrintHook(hook) {
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

    setSendHook(hook) {
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

registerProcessor("{{name}}_AudioLibWorklet", {{name}}_AudioLibWorklet);
