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

#ifndef __JSON2DAISY_FIELD_H__
#define __JSON2DAISY_FIELD_H__

#include "daisy_seed.h"
#include "dev/codec_ak4556.h"
#include "dev/oled_ssd130x.h"

#define ANALOG_COUNT 5

namespace json2daisy {

uint8_t pad_shift_debounced[8*2];
daisy::LedDriverPca9685<2, true>::DmaBuffer DMA_BUFFER_MEM_SECTION led_driver_dma_buffer_a, led_driver_dma_buffer_b;

struct DaisyField {

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
    led_driver.Init(i2c, {0x00, 0x02}, led_driver_dma_buffer_a, led_driver_dma_buffer_b); 
 

    // Switches
    sw1.Init(som.GetPin(30), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP);
    sw2.Init(som.GetPin(29), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED, daisy::Switch::PULL_UP); 
 

    // Muxes
    pad_shift.Init({ som.GetPin(28), som.GetPin(27), { som.GetPin(26) } }); 
 

    // Gate ins
    dsy_gpio_pin gatein_pin = som.GetPin(0);
    gatein.Init(&gatein_pin, true); 
 

    // Single channel ADC initialization
    cfg[0].InitSingle(som.GetPin(17));
    cfg[1].InitSingle(som.GetPin(18));
    cfg[2].InitSingle(som.GetPin(25));
    cfg[3].InitSingle(som.GetPin(24));
    size_t pot_mux_index = 4;
    cfg[pot_mux_index].InitMux(som.GetPin(16), 8, som.GetPin(21), som.GetPin(20), som.GetPin(19)); 
    som.adc.Init(cfg, ANALOG_COUNT);
 

    // AnalogControl objects
    cv1.InitBipolarCv(som.adc.GetPtr(0), som.AudioCallbackRate());
    cv2.InitBipolarCv(som.adc.GetPtr(1), som.AudioCallbackRate());
    cv3.InitBipolarCv(som.adc.GetPtr(2), som.AudioCallbackRate());
    cv4.InitBipolarCv(som.adc.GetPtr(3), som.AudioCallbackRate()); 
 

    // Multiplexed AnlogControl objects
    knob1.Init(som.adc.GetMuxPtr(pot_mux_index, 0), som.AudioCallbackRate(), false, false);
    knob2.Init(som.adc.GetMuxPtr(pot_mux_index, 3), som.AudioCallbackRate(), false, false);
    knob3.Init(som.adc.GetMuxPtr(pot_mux_index, 1), som.AudioCallbackRate(), false, false);
    knob4.Init(som.adc.GetMuxPtr(pot_mux_index, 4), som.AudioCallbackRate(), false, false);
    knob5.Init(som.adc.GetMuxPtr(pot_mux_index, 2), som.AudioCallbackRate(), false, false);
    knob6.Init(som.adc.GetMuxPtr(pot_mux_index, 5), som.AudioCallbackRate(), false, false);
    knob7.Init(som.adc.GetMuxPtr(pot_mux_index, 6), som.AudioCallbackRate(), false, false);
    knob8.Init(som.adc.GetMuxPtr(pot_mux_index, 7), som.AudioCallbackRate(), false, false); 
 

    // Gate outs
    gateout.pin  = som.GetPin(15);
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
         

    som.adc.Start();
  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
 
    cv1.Process();
    cv2.Process();
    cv3.Process();
    cv4.Process();
    knob1.Process();
    knob2.Process();
    knob3.Process();
    knob4.Process();
    knob5.Process();
    knob6.Process();
    knob7.Process();
    knob8.Process();
    sw1.Debounce();
    sw2.Debounce(); 
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    pad_shift.Update();
    pad_shift_debounced[15] = pad_shift.State(15) | (pad_shift_debounced[15] << 1);
    pad_shift_debounced[14] = pad_shift.State(14) | (pad_shift_debounced[14] << 1);
    pad_shift_debounced[13] = pad_shift.State(13) | (pad_shift_debounced[13] << 1);
    pad_shift_debounced[12] = pad_shift.State(12) | (pad_shift_debounced[12] << 1);
    pad_shift_debounced[11] = pad_shift.State(11) | (pad_shift_debounced[11] << 1);
    pad_shift_debounced[10] = pad_shift.State(10) | (pad_shift_debounced[10] << 1);
    pad_shift_debounced[9] = pad_shift.State(9) | (pad_shift_debounced[9] << 1);
    pad_shift_debounced[8] = pad_shift.State(8) | (pad_shift_debounced[8] << 1);
    pad_shift_debounced[7] = pad_shift.State(7) | (pad_shift_debounced[7] << 1);
    pad_shift_debounced[6] = pad_shift.State(6) | (pad_shift_debounced[6] << 1);
    pad_shift_debounced[5] = pad_shift.State(5) | (pad_shift_debounced[5] << 1);
    pad_shift_debounced[4] = pad_shift.State(4) | (pad_shift_debounced[4] << 1);
    pad_shift_debounced[3] = pad_shift.State(3) | (pad_shift_debounced[3] << 1);
    pad_shift_debounced[2] = pad_shift.State(2) | (pad_shift_debounced[2] << 1);
    pad_shift_debounced[1] = pad_shift.State(1) | (pad_shift_debounced[1] << 1);
    pad_shift_debounced[0] = pad_shift.State(0) | (pad_shift_debounced[0] << 1);
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
    cv1.SetSampleRate(som.AudioCallbackRate());
    cv2.SetSampleRate(som.AudioCallbackRate());
    cv3.SetSampleRate(som.AudioCallbackRate());
    cv4.SetSampleRate(som.AudioCallbackRate());
    knob1.SetSampleRate(som.AudioCallbackRate());
    knob2.SetSampleRate(som.AudioCallbackRate());
    knob3.SetSampleRate(som.AudioCallbackRate());
    knob4.SetSampleRate(som.AudioCallbackRate());
    knob5.SetSampleRate(som.AudioCallbackRate());
    knob6.SetSampleRate(som.AudioCallbackRate());
    knob7.SetSampleRate(som.AudioCallbackRate());
    knob8.SetSampleRate(som.AudioCallbackRate());
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
  daisy::AnalogControl cv1;
  daisy::AnalogControl cv2;
  daisy::AnalogControl cv3;
  daisy::AnalogControl cv4;
  daisy::ShiftRegister4021<2> pad_shift;
  daisy::AnalogControl knob1;
  daisy::AnalogControl knob2;
  daisy::AnalogControl knob3;
  daisy::AnalogControl knob4;
  daisy::AnalogControl knob5;
  daisy::AnalogControl knob6;
  daisy::AnalogControl knob7;
  daisy::AnalogControl knob8;
  daisy::DacHandle::Config cvout1;
  daisy::DacHandle::Config cvout2;
  daisy::GateIn gatein;
  dsy_gpio gateout;
  daisy::LedDriverPca9685<2, true> led_driver;
  daisy::Switch sw1;
  daisy::Switch sw2;
  daisy::I2CHandle i2c;
  daisy::OledDisplay<daisy::SSD130x4WireSpi128x64Driver> display;
  daisy::MidiUartHandler midi;

};

} // namspace json2daisy

#endif // __JSON2DAISY_FIELD_H__