# Daisy

To build this code, navigate into the source folder and run `make`.

Flashing can be done over USB with `make program-dfu`. Make sure your Daisy is in DFU mode ([check this out if you're not sure how to do that](https://github.com/electro-smith/DaisyWiki/wiki/1.-Setting-Up-Your-Development-Environment#4-Run-the-Blink-Example)). If you have an ST-Link or other JTAG programmer, you can use `make program`.

If you've made hardware based on the Daisy Seed or Patch Submodule, you can supply custom json for the board description.

# Interacting with the Daisy I/O

Each board has a selection of physical I/O that can interact with your PD patch. Most components have an _alias_, which allows you to refer to the same input/output by different names if you have a preference. All names and aliases are _case insensitive_, so you can style them however you like (e.g. `GateIn`).

Some components have _variants_, which allow you to interact with them in multiple ways. For example, you can receive a bang from a `Gate In` instead of a float if you add `_trig` to the end of the gate's name (or any of its aliases). So, if a `Gate In`'s name is `gatein1`, you would use `gatein1_trig`.

Here's what each component expects for its default behavior and variants:

| Type (_variant) | Behavior |
| --- | --- |
| **Inputs** | --- |
| Voltage Input | Returns a floating point representation of the voltage at its input. The typical range is 0-5 V, which is represented as 0-1. |
| Bipolar Voltage Input | Similar to a regular voltage input, but can represent negative voltages. |
| Switch | Returns a bang on the signal's rising edge (i.e. when the switch is actuated). |
| Switch (_press) | Returns a float representing the current state (1 = pressed, 0 = not pressed) |
| Switch (_fall) | Returns a bang on the signal's falling edge (i.e. when the switch is released). |
| Switch (_seconds) | Returns a float representing the number of seconds the switch has been held down. |
| SPDT Switch | Returns a float representing the current state, either 0 or 1. |
| Encoder | Returns a 1 if turned one direction, -1 if turned in the other, and 0 otherwise. |
| Encoder (\_rise) | Returns a bang when the encoder is pressed. The special alias _EncSwitch_ is always bound to this. |
| Encoder (_press) | Same as switch _press. |
| Encoder (_fall) | Same as switch _fall. |
| Encoder (_seconds) | Same as switch _seconds. |
| Gate In | Returns a float representing the current gate voltage, where a _high_ voltage is 1 and a _low_ voltage is 0. |
| Gate In (_trig) | Returns a bang on the rising edge of the gate signal. |
| **Outputs** | --- |
| CV Out | Expects a floating point value from 0-1, usually converted to 0-5V. |
| Gate Out | Expects a floating point value from 0-1. 0 sets the output low, and 1 sets it high. |
| LED | Expects a floating point value from 0-1. The brightness is PWM modulated to match the input. |
| RGB LED | Expects a floating point value from 0-1. The default behavior sets all three colors to the same brightness. |
| RGB LED (_white) | Same as default. |
| RGB LED (_red) | Expects a floating point value from 0-1. Sets the brightness of the red LED only. |
| RGB LED (_green) | Expects a floating point value from 0-1. Sets the brightness of the green LED only. |
| RGB LED (_blue) | Expects a floating point value from 0-1. Sets the brightness of the blue LED only. |

# Daisy Board I/O

## patch

| Name | Aliases | Type | Variants |
| --- | --- | --- | --- |
| knob1 | knob, ctrl, ctrl1 | Voltage Input | --- |
| knob2 | ctrl2 | Voltage Input | --- |
| knob3 | ctrl3 | Voltage Input | --- |
| knob4 | ctrl4 | Voltage Input | --- |
| encoder | --- | Encoder | encoder_press, encoder_rise, encoder_fall, encoder_seconds |
| gateout | --- | Gate Out | --- |
| cvout1 | cvout | CV Out | --- |
| cvout2 | --- | CV Out | --- |
| gatein1 | gate, gate1 | Gate In | gatein1_trig |
| gatein2 | gate2 | Gate In | gatein2_trig |

## patch_init

| Name | Aliases | Type | Variants |
| --- | --- | --- | --- |
| cv_1 | knob, knob1, ctrl, ctrl1 | Voltage Input | --- |
| cv_2 | knob2, ctrl2 | Voltage Input | --- |
| cv_3 | knob3, ctrl3 | Voltage Input | --- |
| cv_4 | knob4, ctrl4 | Voltage Input | --- |
| cv_5 | knob5, ctrl5 | Voltage Input | --- |
| cv_6 | knob6, ctrl6 | Voltage Input | --- |
| cv_7 | knob7, ctrl7 | Voltage Input | --- |
| cv_8 | knob8, ctrl8 | Voltage Input | --- |
| adc_9 | --- | Voltage Input | --- |
| adc_10 | --- | Voltage Input | --- |
| adc_11 | --- | Voltage Input | --- |
| adc_12 | --- | Voltage Input | --- |
| gate_out_1 | gateout, gateout1 | Gate Out | --- |
| gate_out_2 | gateout2 | Gate Out | --- |
| cvout1 | cvout, cv_out_1 | CV Out | --- |
| cvout2 | cv_out_2 | CV Out | --- |
| gate_in_1 | gate, gate1 | Gate In | gate_in_1_trig |
| gate_in_2 | gate2 | Gate In | gate_in_2_trig |
| sw1 | switch, switch1, button | Switch | sw1_press, sw1_fall, sw1_seconds |
| sw2 | switch2, toggle | Switch | sw2_press, sw2_fall, sw2_seconds |

## petal

| Name | Aliases | Type | Variants |
| --- | --- | --- | --- |
| sw1 | switch, switch1 | Switch | sw1_press, sw1_fall, sw1_seconds |
| sw2 | switch2 | Switch | sw2_press, sw2_fall, sw2_seconds |
| sw3 | switch3 | Switch | sw3_press, sw3_fall, sw3_seconds |
| sw4 | switch4 | Switch | sw4_press, sw4_fall, sw4_seconds |
| sw5 | switch5 | Switch | sw5_press, sw5_fall, sw5_seconds |
| sw6 | switch6 | Switch | sw6_press, sw6_fall, sw6_seconds |
| sw7 | switch7 | Switch | sw7_press, sw7_fall, sw7_seconds |
| encoder | --- | Encoder | encoder_press, encoder_rise, encoder_fall, encoder_seconds |
| knob1 | knob, ctrl, ctrl1 | Voltage Input | --- |
| knob2 | ctrl2 | Voltage Input | --- |
| knob3 | ctrl3 | Voltage Input | --- |
| knob4 | ctrl4 | Voltage Input | --- |
| knob5 | ctrl5 | Voltage Input | --- |
| knob6 | ctrl6 | Voltage Input | --- |
| expression | --- | Voltage Input | --- |
| led_ring_1 ... led_ring_8 | --- | RGB LED | led_ring_1_red, led_ring_1_green, led_ring_1_blue, led_ring_1_white |
| led_fs_1 | --- | LED | --- |
| led_fs_2 | --- | LED | --- |
| led_fs_3 | --- | LED | --- |
| led_fs_4 | --- | LED | --- |

## pod

| Name | Aliases | Type | Variants |
| --- | --- | --- | --- |
| sw1 | switch, button, switch1, button1 | Switch | sw1_press, sw1_fall, sw1_seconds |
| sw2 | switch2, button2 | Switch | sw2_press, sw2_fall, sw2_seconds |
| knob1 | knob, ctrl, ctrl1 | Voltage Input | --- |
| knob2 | ctrl2 | Voltage Input | --- |
| encoder | --- | Encoder | encoder_press, encoder_rise, encoder_fall, encoder_seconds |
| led1 | led | RGB LED | led1_red, led1_green, led1_blue, led1_white |
| led2 | --- | RGB LED | led2_red, led2_green, led2_blue, led2_white |
| led3 | --- | LED | --- |
| cvout1 | cvout | CV Out | --- |
| gatein | gate, gate1 | Gate In | gatein_trig |
| sw3 | switch3 | SPDT Switch | --- |

## field

| Name | Aliases | Type | Variants |
| --- | --- | --- | --- |
| sw1 | switch, button, switch1, button1 | Switch | sw1_press, sw1_fall, sw1_seconds |
| sw2 | switch2, button2 | Switch | sw2_press, sw2_fall, sw2_seconds |
| cv1 | --- | Bipolar Voltage Input | --- |
| cv2 | --- | Bipolar Voltage Input | --- |
| cv3 | --- | Bipolar Voltage Input | --- |
| cv4 | --- | Bipolar Voltage Input | --- |
| knob1 | knob, ctrl, ctrl1 | Voltage Input | --- |
| knob2 | ctrl2 | Voltage Input | --- |
| knob3 ... knob8 | --- | Voltage Input | --- |
| cvout1 | cvout | CV Out | --- |
| cvout2 | --- | CV Out | --- |
| gatein | --- | Gate In | gatein_trig |
| gateout | --- | Gate Out | --- |
| pada1 ... pada8 | --- | Switch | pada1_press, pada1_fall |
| padb1 ... padb8 | --- | Switch | padb1_press, padb1_fall |
| led_key_a1 ... led_key_a8 | --- | LED | --- |
| led_key_b1 ... led_key_b8 | --- | LED | --- |
| led_knob_1 ... led_knob_8 | --- | LED | --- |
| led_sw_1 | --- | LED | --- |
| led_sw_2 | --- | LED | --- |
