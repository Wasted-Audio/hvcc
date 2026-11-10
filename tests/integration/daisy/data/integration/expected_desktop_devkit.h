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

#ifndef __JSON2DAISY_DESKTOP_DEVKIT_H__
#define __JSON2DAISY_DESKTOP_DEVKIT_H__

#include "daisy_seed.h"
#include "dev/codec_ak4556.h"


#define ANALOG_COUNT 3

namespace json2daisy {

uint8_t button_sr_debounced[8*2];
daisy::LedDriverPca9685<1, true>::DmaBuffer DMA_BUFFER_MEM_SECTION led_driver_dma_buffer_a, led_driver_dma_buffer_b;

struct DaisyDesktop_devkit {

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
    led_driver.Init(i2c, {0x00}, led_driver_dma_buffer_a, led_driver_dma_buffer_b);

    // Switches
    sw17.Init(som.GetPin(19), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED);
    detect_l.Init(som.GetPin(16), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_NORMAL);
    detect_r.Init(som.GetPin(17), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_NORMAL);
    sd_detect.Init(som.GetPin(7), som.AudioCallbackRate(), daisy::Switch::TYPE_MOMENTARY, daisy::Switch::POLARITY_INVERTED);

    // SPDT Switches
    sw18.Init(som.GetPin(28), som.GetPin(27));

    // Muxes
    button_sr.Init({ som.GetPin(8), som.GetPin(9), { som.GetPin(10) }, 10 });

    // Gate ins
    gate_in1.Init(som.GetPin(0), true);
    gate_in2.Init(som.GetPin(18), true);

    // Single channel ADC initialization
    cfg[0].InitSingle(som.GetPin(20));
    cfg[1].InitSingle(som.GetPin(21));
    size_t pot_mux_index = 2;
    cfg[pot_mux_index].InitMux(som.GetPin(15), 8, som.GetPin(24), som.GetPin(25), som.GetPin(26));
    som.adc.Init(cfg, ANALOG_COUNT);

    // AnalogControl objects
    cv1.InitBipolarCv(som.adc.GetPtr(0), som.AudioCallbackRate());
    cv2.InitBipolarCv(som.adc.GetPtr(1), som.AudioCallbackRate());

    // Multiplexed AnlogControl objects
    pot1.Init(som.adc.GetMuxPtr(pot_mux_index, 0), som.AudioCallbackRate(), false, false);
    pot2.Init(som.adc.GetMuxPtr(pot_mux_index, 1), som.AudioCallbackRate(), false, false);
    pot3.Init(som.adc.GetMuxPtr(pot_mux_index, 2), som.AudioCallbackRate(), false, false);
    pot4.Init(som.adc.GetMuxPtr(pot_mux_index, 3), som.AudioCallbackRate(), false, false);
    pot5.Init(som.adc.GetMuxPtr(pot_mux_index, 4), som.AudioCallbackRate(), false, false);
    pot6.Init(som.adc.GetMuxPtr(pot_mux_index, 5), som.AudioCallbackRate(), false, false);
    pot7.Init(som.adc.GetMuxPtr(pot_mux_index, 6), som.AudioCallbackRate(), false, false);
    pot8.Init(som.adc.GetMuxPtr(pot_mux_index, 7), som.AudioCallbackRate(), false, false);

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

    som.adc.Start();
  }

  /** Handles all the controls processing that needs to occur at the block rate
   *
   */
  void ProcessAllControls()
  {
    cv1.Process();
    cv2.Process();
    pot1.Process();
    pot2.Process();
    pot3.Process();
    pot4.Process();
    pot5.Process();
    pot6.Process();
    pot7.Process();
    pot8.Process();
    sw17.Debounce();
    detect_l.Debounce();
    detect_r.Debounce();
    sd_detect.Debounce();
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   *
   */
  void PostProcess()
  {
    button_sr.Update();
    button_sr_debounced[15] = button_sr.State(15) | (button_sr_debounced[15] << 1);
    button_sr_debounced[14] = button_sr.State(14) | (button_sr_debounced[14] << 1);
    button_sr_debounced[13] = button_sr.State(13) | (button_sr_debounced[13] << 1);
    button_sr_debounced[12] = button_sr.State(12) | (button_sr_debounced[12] << 1);
    button_sr_debounced[11] = button_sr.State(11) | (button_sr_debounced[11] << 1);
    button_sr_debounced[10] = button_sr.State(10) | (button_sr_debounced[10] << 1);
    button_sr_debounced[9] = button_sr.State(9) | (button_sr_debounced[9] << 1);
    button_sr_debounced[8] = button_sr.State(8) | (button_sr_debounced[8] << 1);
    button_sr_debounced[7] = button_sr.State(7) | (button_sr_debounced[7] << 1);
    button_sr_debounced[6] = button_sr.State(6) | (button_sr_debounced[6] << 1);
    button_sr_debounced[5] = button_sr.State(5) | (button_sr_debounced[5] << 1);
    button_sr_debounced[4] = button_sr.State(4) | (button_sr_debounced[4] << 1);
    button_sr_debounced[3] = button_sr.State(3) | (button_sr_debounced[3] << 1);
    button_sr_debounced[2] = button_sr.State(2) | (button_sr_debounced[2] << 1);
    button_sr_debounced[1] = button_sr.State(1) | (button_sr_debounced[1] << 1);
    button_sr_debounced[0] = button_sr.State(0) | (button_sr_debounced[0] << 1);
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
    pot1.SetSampleRate(som.AudioCallbackRate());
    pot2.SetSampleRate(som.AudioCallbackRate());
    pot3.SetSampleRate(som.AudioCallbackRate());
    pot4.SetSampleRate(som.AudioCallbackRate());
    pot5.SetSampleRate(som.AudioCallbackRate());
    pot6.SetSampleRate(som.AudioCallbackRate());
    pot7.SetSampleRate(som.AudioCallbackRate());
    pot8.SetSampleRate(som.AudioCallbackRate());
    sw17.SetUpdateRate(som.AudioCallbackRate());
    detect_l.SetUpdateRate(som.AudioCallbackRate());
    detect_r.SetUpdateRate(som.AudioCallbackRate());
    sd_detect.SetUpdateRate(som.AudioCallbackRate());
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
  daisy::ShiftRegister4021<2> button_sr;
  daisy::AnalogControl pot1;
  daisy::AnalogControl pot2;
  daisy::AnalogControl pot3;
  daisy::AnalogControl pot4;
  daisy::AnalogControl pot5;
  daisy::AnalogControl pot6;
  daisy::AnalogControl pot7;
  daisy::AnalogControl pot8;
  daisy::DacHandle::Config cvout1;
  daisy::DacHandle::Config cvout2;
  daisy::GateIn gate_in1;
  daisy::GateIn gate_in2;
  daisy::LedDriverPca9685<1, true> led_driver;
  daisy::Switch sw17;
  daisy::Switch detect_l;
  daisy::Switch detect_r;
  daisy::Switch sd_detect;
  daisy::Switch3 sw18;
  daisy::I2CHandle i2c;

  daisy::MidiUartHandler midi;

};

} // namspace json2daisy

#endif // __JSON2DAISY_DESKTOP_DEVKIT_H__
