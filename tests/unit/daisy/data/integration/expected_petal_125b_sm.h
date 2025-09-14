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

#ifndef __JSON2DAISY_PETAL_125B_SM_H__
#define __JSON2DAISY_PETAL_125B_SM_H__

#include "daisy_petal_125b_sm.h"


#define ANALOG_COUNT 6

namespace json2daisy {



struct DaisyPetal_125b_sm {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    som.Init();

    // i2c
     
 

    // LED Drivers
     
 

    // Switches
    
     

    // SPDT Switches
    
    
     
 

    // Muxes
     
 

    // Gate ins
     
 

    // Rotary encoders
     
 

    // Single channel ADC initialization
    
    
    
    
    
     
 

    // AnalogControl objects
    
    
    
    
    
     
 

    // Multiplexed AnlogControl objects
     

    // RBG LEDs 
    
     
 

    // Gate outs
     

    // DAC 
     

    // Adafruit Motor Shield
    

    // Stepper motor pointer from the Adafruit Motor Shield
    

    // DC motor pointer from the Adafruit Motor Shield
    

    // BME280 pressure/temperature/humidity sensor
    

    // Hall sensor
    

    // Accelerometer
    

    // Capacitive sensor
    

    // Gesture / color sensor
    

    // Bmp390 pressure / temperature sensor
    

    // Dps310 pressure / temperature sensor
    

    // Vl53l1x time of flight sensor
    

    // Vl53l0x time of flight sensor
    

    // Adafruit Neo Trellis
    

    // Bno055 9-DOF omega sensor
    

    // Icm20948 9-DOF sensor
    

  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
    som.ProcessAllControls();
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    
    som.UpdateLeds();
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
  daisy::Petal125BSM som;

  // I/O Components
  
  
  

};

} // namspace json2daisy

#endif // __JSON2DAISY_PETAL_125B_SM_H__