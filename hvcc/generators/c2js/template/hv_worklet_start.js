
// Some hacks gathered from this thread: https://github.com/emscripten-core/emscripten/issues/6230
var self = {
  location: {
      href: "http://localhost:3000/" // URL where the module was loaded from
  }
};

function importScripts(){
  console.warn('importScripts should not be called in an AudioWorklet', arguments);
}