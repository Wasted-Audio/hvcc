/*
 * MIT License
 * 
 * Copyright (c) 2021 Electrosmith
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * 
 */

#ifndef __JSON2DAISY_POD_H__
#define __JSON2DAISY_POD_H__

#include "daisy_seed.h"
#include "dev/codec_ak4556.h"
#include "dev/oled_ssd130x.h"

#define ANALOG_COUNT 2

namespace json2daisy {



struct DaisyPod {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    som.Configure();
    som.Init(boost);
 

    // Switches
    sw1.Init(som.GetPin(27), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw2.Init(som.GetPin(28), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP); 
 

    // Rotary encoders
    encoder.Init(som.GetPin(26), som.GetPin(25), som.GetPin(13), som.AudioCallbackRate()); 
 

    // Single channel ADC initialization
    cfg[0].InitSingle(som.GetPin(21));
    cfg[1].InitSingle(som.GetPin(15)); 
    som.adc.Init(cfg, ANALOG_COUNT);
 

    // AnalogControl objects
    knob1.Init(som.adc.GetPtr(0), som.AudioCallbackRate(), false, false);
    knob2.Init(som.adc.GetPtr(1), som.AudioCallbackRate(), false, false); 

    // RBG LEDs 
    led1.Init(som.GetPin(20), som.GetPin(19), som.GetPin(18), true);
    led1.Set(0.0f, 0.0f, 0.0f);
    led2.Init(som.GetPin(17), som.GetPin(24), som.GetPin(23), true);
    led2.Set(0.0f, 0.0f, 0.0f); 

    // Display
    
        daisy::OledDisplay<daisy::SSD130x4WireSpi128x64Driver>::Config display_config;
        display_config.driver_config.transport_config.Defaults();
        
        display.Init(display_config);
          display.Fill(0);
          display.Update();
         

    som.adc.Start();
  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
 
    knob1.Process();
    knob2.Process();
    encoder.Debounce();
    sw1.Debounce();
    sw2.Debounce(); 
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    led1.Update();
    led2.Update();
  }

  /** Handles processing that shouldn't occur in the audio block, such as blocking transfers
   * 
   */
  void LoopProcess()
  {
    
  }

  /** Sets the audio sample rate
   *  \param sample_rate the new sample rate in Hz
   */
  void SetAudioSampleRate(size_t sample_rate) 
  {
    daisy::SaiHandle::Config::SampleRate enum_rate;
    if (sample_rate >= 96000)
      enum_rate = daisy::SaiHandle::Config::SampleRate::SAI_96KHZ;
    else if (sample_rate >= 48000)
      enum_rate = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    else if (sample_rate >= 32000)
      enum_rate = daisy::SaiHandle::Config::SampleRate::SAI_32KHZ;
    else if (sample_rate >= 16000)
      enum_rate = daisy::SaiHandle::Config::SampleRate::SAI_16KHZ;
    else
      enum_rate = daisy::SaiHandle::Config::SampleRate::SAI_8KHZ;
    som.SetAudioSampleRate(enum_rate);
    knob1.SetSampleRate(som.AudioCallbackRate());
    knob2.SetSampleRate(som.AudioCallbackRate());
    encoder.SetUpdateRate(som.AudioCallbackRate());
    sw1.SetUpdateRate(som.AudioCallbackRate());
    sw2.SetUpdateRate(som.AudioCallbackRate());
  }

  /** Sets the audio block size
   *  \param block_size the new block size in words
   */
  inline void SetAudioBlockSize(size_t block_size) 
  {
    som.SetAudioBlockSize(block_size);
  }

  /** Starts up the audio callback process with the given callback
   * 
   */
  inline void StartAudio(daisy::AudioHandle::AudioCallback cb)
  {
    som.StartAudio(cb);
  }

  /** This is the board's "System On Module" */
  daisy::DaisySeed som;
  daisy::AdcChannelConfig cfg[ANALOG_COUNT];

  // I/O Components
  daisy::AnalogControl knob1;
  daisy::AnalogControl knob2;
  daisy::Encoder encoder;
  daisy::RgbLed led1;
  daisy::RgbLed led2;
  daisy::Switch sw1;
  daisy::Switch sw2;
  daisy::OledDisplay<daisy::SSD130x4WireSpi128x64Driver> display;
  daisy::MidiUartHandler midi;

};

} // namspace json2daisy

#endif // __JSON2DAISY_POD_H__