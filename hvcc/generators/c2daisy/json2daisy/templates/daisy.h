{{license}}

#ifndef __JSON2DAISY_{{name|upper}}_H__
#define __JSON2DAISY_{{name|upper}}_H__

{% if som == 'seed' %}
#include "daisy_seed.h"
#include "dev/codec_ak4556.h"
{% elif som == 'patch_sm' %}
#include "daisy_patch_sm.h"
{% elif som == 'petal_125b_sm' %}
#include "daisy_petal_125b_sm.h"
{% endif %}
{{display_conditional}}

#define ANALOG_COUNT {{analogcount}}

namespace json2daisy {

{{non_class_declarations}}

struct Daisy{{ name|capitalize }} {

  /** Initializes the board according to the JSON board description
   *  \param boost boosts the clock speed from 400 to 480 MHz
   */
  void Init(bool boost=true) 
  {
    {% if som == 'seed' %}
    som.Configure();
    som.Init(boost);
    {% else %}
    som.Init();
    {% endif %}
    {% if init != '' %} 

    {{init}} 
    {% endif %}
    {% if i2c != '' %}

    // i2c
    {{ i2c }} 
    {% endif %}
    {% if PCA9685 != '' %} 

    // LED Drivers
    {{ PCA9685 }} 
    {% endif %}
    {% if Switch != '' %} 

    // Switches
    {{ Switch }} 
    {% endif %}
    {% if Switch3 != '' %}

    // SPDT Switches
    {{ Switch3 }} 
    {% endif %}
    {% if CD4021 != '' %} 

    // Muxes
    {{ CD4021 }} 
    {% endif %}
    {% if GateIn != '' %} 

    // Gate ins
    {{ GateIn }} 
    {% endif %}
    {% if Encoder != '' %} 

    // Rotary encoders
    {{ Encoder }} 
    {% endif %}
    {% if init_single != '' %} 

    // Single channel ADC initialization
    {{ init_single }} 
    {% endif %}
    {% if som == 'seed' %}
    {% if analogcount > 0 %}
    som.adc.Init(cfg, ANALOG_COUNT);
    {% endif %}
    {% endif %}
    {% if ctrl_init != '' %} 

    // AnalogControl objects
    {{ ctrl_init }} 
    {% endif %}
    {% if CD4051AnalogControl != '' %} 

    // Multiplexed AnlogControl objects
    {{ CD4051AnalogControl }} 
    {% endif %}
    {% if Led != '' %} 

    // LEDs
    {{ Led }} 
    {% endif %}
    {% if RgbLed != '' %}

    // RBG LEDs 
    {{ RgbLed }} 
    {% endif %}
    {% if GateOut != '' %} 

    // Gate outs
    {{ GateOut }} 
    {% endif %}
    {% if CVOuts != '' %}

    // DAC 
    {{ CVOuts }} 
    {% endif %}
    {% if display != '' %}

    // Display
    {{ display }} 
    {% endif %}
    {% if MotorShield != '' %}

    // Adafruit Motor Shield
    {{ MotorShield }}
    {% endif %}
    {% if StepperMotor != '' %}

    // Stepper motor pointer from the Adafruit Motor Shield
    {{ StepperMotor }}
    {% endif %}
    {% if DcMotor != '' %}

    // DC motor pointer from the Adafruit Motor Shield
    {{ DcMotor }}
    {% endif %}
    {% if Bme280 != '' %}

    // BME280 pressure/temperature/humidity sensor
    {{ Bme280 }}
    {% endif %}
    {% if HallSensor != '' %}

    // Hall sensor
    {{ HallSensor }}
    {% endif %}
    {% if Tlv493d != '' %}

    // Accelerometer
    {{ Tlv493d }}
    {% endif %}
    {% if Mpr121 != '' %}

    // Capacitive sensor
    {{ Mpr121 }}
    {% endif %}
    {% if Apds9960 != '' %}

    // Gesture / color sensor
    {{ Apds9960 }}
    {% endif %}
    {% if Bmp390 != '' %}

    // Bmp390 pressure / temperature sensor
    {{ Bmp390 }}
    {% endif %}
    {% if Dps310 != '' %}

    // Dps310 pressure / temperature sensor
    {{ Dps310 }}
    {% endif %}
    {% if Vl53l1x != '' %}

    // Vl53l1x time of flight sensor
    {{ Vl53l1x }}
    {% endif %}
    {% if Vl53l0x != '' %}

    // Vl53l0x time of flight sensor
    {{ Vl53l0x }}
    {% endif %}
    {% if NeoTrellis != '' %}

    // Adafruit Neo Trellis
    {{ NeoTrellis }}
    {% endif %}
    {% if Bno055 != '' %}

    // Bno055 9-DOF omega sensor
    {{ Bno055 }}
    {% endif %}
    {% if Icm20948 != '' %}

    // Icm20948 9-DOF sensor
    {{ Icm20948 }}
    {% endif %}
    {% if som == 'seed' and external_codecs|length > 0 %}

    // External Codec Initialization
    daisy::SaiHandle::Config sai_config[{{ 1 + external_codecs|length }}];

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

    {% for codec in external_codecs %}
    sai_config[{{loop.index}}].periph          = daisy::SaiHandle::Config::Peripheral::{{codec.periph}};
    sai_config[{{loop.index}}].sr              = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    sai_config[{{loop.index}}].bit_depth       = daisy::SaiHandle::Config::BitDepth::SAI_24BIT;
    sai_config[{{loop.index}}].a_sync          = daisy::SaiHandle::Config::Sync::{{codec.a_sync}};
    sai_config[{{loop.index}}].b_sync          = daisy::SaiHandle::Config::Sync::{{codec.b_sync}};
    sai_config[{{loop.index}}].a_dir           = daisy::SaiHandle::Config::Direction::{{codec.a_dir}};
    sai_config[{{loop.index}}].b_dir           = daisy::SaiHandle::Config::Direction::{{codec.b_dir}};
    sai_config[{{loop.index}}].pin_config.fs   = som.GetPin({{codec.pin.fs}});
    sai_config[{{loop.index}}].pin_config.mclk = som.GetPin({{codec.pin.mclk}});
    sai_config[{{loop.index}}].pin_config.sck  = som.GetPin({{codec.pin.sck}});
    sai_config[{{loop.index}}].pin_config.sa   = som.GetPin({{codec.pin.sa}});
    sai_config[{{loop.index}}].pin_config.sb   = som.GetPin({{codec.pin.sb}});
    {% endfor %}

    daisy::SaiHandle sai_handle[{{ 1 + external_codecs|length }}];
    sai_handle[0].Init(sai_config[0]);
    {% for codec in external_codecs %}
    sai_handle[{{loop.index}}].Init(sai_config[{{loop.index}}]);
    {% endfor %}

    dsy_gpio_pin codec_reset_pin = som.GetPin(29);
    daisy::Ak4556::Init(codec_reset_pin);

    daisy::AudioHandle::Config cfg;
    cfg.blocksize  = 48;
    cfg.samplerate = daisy::SaiHandle::Config::SampleRate::SAI_48KHZ;
    cfg.postgain   = 0.5f;
    som.audio_handle.Init(
      cfg, 
      sai_handle[0]
      {% for codec in external_codecs %}
      ,sai_handle[{{loop.index}}]
      {% endfor %}
    );
    {% endif %}

    {% if som == 'seed' %}
    {% if analogcount > 0 %}
    som.adc.Start();
    {% endif %}
    {% endif %}
  }

  /** Handles all the controls processing that needs to occur at the block rate
   * 
   */
  void ProcessAllControls() 
  {
    {% if process != '' %} 
    {{ process }} 
    {% endif %}
    {% if som != 'seed' %}
    som.ProcessAllControls();
    {% endif %}
  }

  /** Handles all the maintenance processing. This should be run last within the audio callback.
   * 
   */
  void PostProcess()
  {
    {{postprocess}}
    {% if som == 'petal_125b_sm' %}
    som.UpdateLeds();
    {% endif %}
  }

  /** Handles processing that shouldn't occur in the audio block, such as blocking transfers
   * 
   */
  void LoopProcess()
  {
    {{loopprocess}}
  }

  /** Sets the audio sample rate
   *  \param sample_rate the new sample rate in Hz
   */
  void SetAudioSampleRate(size_t sample_rate) 
  {
    {% if som == 'seed' or som == 'petal_125b_sm' %}
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
    {% elif som == 'patch_sm' %}
    som.SetAudioSampleRate(sample_rate);
    {% endif %}
    {{hidupdaterates}}
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
  {{som_class}} som;
  {% if som == 'seed' %}
  daisy::AdcChannelConfig cfg[ANALOG_COUNT];
  {% endif %}

  // I/O Components
  {{comps}}
  {{dispdec}}
  {{midi}}

};

} // namspace json2daisy

#endif // __JSON2DAISY_{{name|upper}}_H__
