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

#ifndef __JSON2DAISY_PATCH_H__
#define __JSON2DAISY_PATCH_H__

#include "daisy_seed.h"
#include "dev/codec_ak4556.h"
#include "dev/oled_ssd130x.h"

#define ANALOG_COUNT 4

namespace json2daisy {



struct DaisyPatch {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    som.Configure();
    som.Init(boost);
 

    // Gate ins
    dsy_gpio_pin gatein1_pin = som.GetPin(20);
    gatein1.Init(&gatein1_pin, true);
    dsy_gpio_pin gatein2_pin = som.GetPin(19);
    gatein2.Init(&gatein2_pin, true); 
 

    // Rotary encoders
    encoder.Init(som.GetPin(12), som.GetPin(11), som.GetPin(0), som.AudioCallbackRate()); 
 

    // Single channel ADC initialization
    cfg[0].InitSingle(som.GetPin(15));
    cfg[1].InitSingle(som.GetPin(16));
    cfg[2].InitSingle(som.GetPin(21));
    cfg[3].InitSingle(som.GetPin(18)); 
    som.adc.Init(cfg, ANALOG_COUNT);
 

    // AnalogControl objects
    knob1.Init(som.adc.GetPtr(0), som.AudioCallbackRate(), true, false);
    knob2.Init(som.adc.GetPtr(1), som.AudioCallbackRate(), true, false);
    knob3.Init(som.adc.GetPtr(2), som.AudioCallbackRate(), true, false);
    knob4.Init(som.adc.GetPtr(3), som.AudioCallbackRate(), true, false); 
 

    // Gate outs
    gateout.pin  = som.GetPin(17);
    gateout.mode = DSY_GPIO_MODE_OUTPUT_PP;
    gateout.pull = DSY_GPIO_NOPULL;
    dsy_gpio_init(&gateout); 

    // DAC 
    cvout1.bitdepth = daisy::DacHandle::BitDepth::BITS_12;
    cvout1.buff_state = daisy::DacHandle::BufferState::ENABLED;
    cvout1.mode = daisy::DacHandle::Mode::POLLING;
    cvout1.chn = daisy::DacHandle::Channel::BOTH;
    som.dac.Init(cvout1);
    som.dac.WriteValue(daisy::DacHandle::Channel::BOTH, 0);
    cvout2.bitdepth = daisy::DacHandle::BitDepth::BITS_12;
    cvout2.buff_state = daisy::DacHandle::BufferState::ENABLED;
    cvout2.mode = daisy::DacHandle::Mode::POLLING;
    cvout2.chn = daisy::DacHandle::Channel::BOTH;
    som.dac.Init(cvout2);
    som.dac.WriteValue(daisy::DacHandle::Channel::BOTH, 0); 

    // Display
    
        daisy::OledDisplay<daisy::SSD130x4WireSpi128x64Driver>::Config display_config;
        display_config.driver_config.transport_config.Defaults();
        
        display.Init(display_config);
          display.Fill(0);
          display.Update();
         

    // External Codec Initialization
    daisy::SaiHandle::Config sai_config[2];

    // Internal Codec
    sai_config[0].periph          = daisy::SaiHandle::Config::Peripheral::SAI_1;
    sai_config[0].sr              = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[0].bit_depth       = daisy::SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[0].a_sync          = daisy::SaiHandle::Config::Sync::MASTER;
    sai_config[0].b_sync          = daisy::SaiHandle::Config::Sync::SLAVE;
    sai_config[0].a_dir           = daisy::SaiHandle::Config::Direction::TRANSMIT;
    sai_config[0].b_dir           = daisy::SaiHandle::Config::Direction::RECEIVE;
    sai_config[0].pin_config.fs   = {DSY_GPIOE, 4};
    sai_config[0].pin_config.mclk = {DSY_GPIOE, 2};
    sai_config[0].pin_config.sck  = {DSY_GPIOE, 5};
    sai_config[0].pin_config.sa   = {DSY_GPIOE, 6};
    sai_config[0].pin_config.sb   = {DSY_GPIOE, 3};

    sai_config[1].periph          = daisy::SaiHandle::Config::Peripheral::SAI_2;
    sai_config[1].sr              = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[1].bit_depth       = daisy::SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[1].a_sync          = daisy::SaiHandle::Config::Sync::SLAVE;
    sai_config[1].b_sync          = daisy::SaiHandle::Config::Sync::MASTER;
    sai_config[1].a_dir           = daisy::SaiHandle::Config::Direction::TRANSMIT;
    sai_config[1].b_dir           = daisy::SaiHandle::Config::Direction::RECEIVE;
    sai_config[1].pin_config.fs   = som.GetPin(27);
    sai_config[1].pin_config.mclk = som.GetPin(24);
    sai_config[1].pin_config.sck  = som.GetPin(28);
    sai_config[1].pin_config.sa   = som.GetPin(26);
    sai_config[1].pin_config.sb   = som.GetPin(25);

    daisy::SaiHandle sai_handle[2];
    sai_handle[0].Init(sai_config[0]);
    sai_handle[1].Init(sai_config[1]);

    dsy_gpio_pin codec_reset_pin = som.GetPin(29);
    daisy::Ak4556::Init(codec_reset_pin);

    daisy::AudioHandle::Config cfg;
    cfg.blocksize  = 48;
    cfg.samplerate = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    cfg.postgain   = 0.5f;
    som.audio_handle.Init(
      cfg, 
      sai_handle[0]
      ,sai_handle[1]
    );

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
    encoder.Debounce(); 
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
    encoder.SetUpdateRate(som.AudioCallbackRate());
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
  daisy::DacHandle::Config cvout1;
  daisy::DacHandle::Config cvout2;
  daisy::Encoder encoder;
  daisy::GateIn gatein1;
  daisy::GateIn gatein2;
  dsy_gpio gateout;
  daisy::OledDisplay<daisy::SSD130x4WireSpi128x64Driver> display;
  daisy::MidiUartHandler midi;

};

} // namspace json2daisy

#endif // __JSON2DAISY_PATCH_H__