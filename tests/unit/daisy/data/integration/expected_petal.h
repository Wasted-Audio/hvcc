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

#ifndef __JSON2DAISY_PETAL_H__
#define __JSON2DAISY_PETAL_H__

#include "daisy_seed.h"
#include "dev/codec_ak4556.h"


#define ANALOG_COUNT 7

namespace json2daisy {

daisy::LedDriverPca9685<2, true>::DmaBuffer DMA_BUFFER_MEM_SECTION led_driver_dma_buffer_a, led_driver_dma_buffer_b;

struct DaisyPetal {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    som.Configure();
    som.Init(boost);

    // i2c
    i2c.Init({daisy::I2CHandle::Config::Peripheral::I2C_1, {som.GetPin(11), som.GetPin(12)}, daisy::I2CHandle::Config::Speed::I2C_1MHZ, daisy::I2CHandle::Config::Mode::I2C_MASTER}); 
 

    // LED Drivers
    led_driver.Init(i2c, {0x00, 0x01}, led_driver_dma_buffer_a, led_driver_dma_buffer_b); 
 

    // Switches
    sw1.Init(som.GetPin(8), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw2.Init(som.GetPin(9), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw3.Init(som.GetPin(10), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw4.Init(som.GetPin(13), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw5.Init(som.GetPin(25), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw6.Init(som.GetPin(26), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw7.Init(som.GetPin(7), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP); 
 

    // Rotary encoders
    encoder.Init(som.GetPin(28), som.GetPin(27), som.GetPin(14), som.AudioCallbackRate()); 
 

    // Single channel ADC initialization
    cfg[0].InitSingle(som.GetPin(16));
    cfg[1].InitSingle(som.GetPin(19));
    cfg[2].InitSingle(som.GetPin(17));
    cfg[3].InitSingle(som.GetPin(20));
    cfg[4].InitSingle(som.GetPin(18));
    cfg[5].InitSingle(som.GetPin(21));
    cfg[6].InitSingle(som.GetPin(15)); 
    som.adc.Init(cfg, ANALOG_COUNT);
 

    // AnalogControl objects
    knob1.Init(som.adc.GetPtr(0), som.AudioCallbackRate(), false, false);
    knob2.Init(som.adc.GetPtr(1), som.AudioCallbackRate(), false, false);
    knob3.Init(som.adc.GetPtr(2), som.AudioCallbackRate(), false, false);
    knob4.Init(som.adc.GetPtr(3), som.AudioCallbackRate(), false, false);
    knob5.Init(som.adc.GetPtr(4), som.AudioCallbackRate(), false, false);
    knob6.Init(som.adc.GetPtr(5), som.AudioCallbackRate(), false, false);
    expression.Init(som.adc.GetPtr(6), som.AudioCallbackRate(), false, false); 

    som.adc.Start();
  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
 
    knob1.Process();
    knob2.Process();
    knob3.Process();
    knob4.Process();
    knob5.Process();
    knob6.Process();
    expression.Process();
    encoder.Debounce();
    sw1.Debounce();
    sw2.Debounce();
    sw3.Debounce();
    sw4.Debounce();
    sw5.Debounce();
    sw6.Debounce();
    sw7.Debounce(); 
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    
  }

  /** Handles processing that shouldn't occur in the audio block, such as blocking transfers
   * 
   */
  void LoopProcess()
  {
    led_driver.SwapBuffersAndTransmit();
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
    knob3.SetSampleRate(som.AudioCallbackRate());
    knob4.SetSampleRate(som.AudioCallbackRate());
    knob5.SetSampleRate(som.AudioCallbackRate());
    knob6.SetSampleRate(som.AudioCallbackRate());
    expression.SetSampleRate(som.AudioCallbackRate());
    encoder.SetUpdateRate(som.AudioCallbackRate());
    sw1.SetUpdateRate(som.AudioCallbackRate());
    sw2.SetUpdateRate(som.AudioCallbackRate());
    sw3.SetUpdateRate(som.AudioCallbackRate());
    sw4.SetUpdateRate(som.AudioCallbackRate());
    sw5.SetUpdateRate(som.AudioCallbackRate());
    sw6.SetUpdateRate(som.AudioCallbackRate());
    sw7.SetUpdateRate(som.AudioCallbackRate());
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
  daisy::AnalogControl knob3;
  daisy::AnalogControl knob4;
  daisy::AnalogControl knob5;
  daisy::AnalogControl knob6;
  daisy::AnalogControl expression;
  daisy::Encoder encoder;
  daisy::LedDriverPca9685<2, true> led_driver;
  daisy::Switch sw1;
  daisy::Switch sw2;
  daisy::Switch sw3;
  daisy::Switch sw4;
  daisy::Switch sw5;
  daisy::Switch sw6;
  daisy::Switch sw7;
  daisy::I2CHandle i2c;
  
  

};

} // namspace json2daisy

#endif // __JSON2DAISY_PETAL_H__