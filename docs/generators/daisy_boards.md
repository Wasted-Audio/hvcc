# Daisy Board I/O

An overview of the standard Electro-Smith prototyping devices and their included [Board JSON](daisy_json.md) layout.

You can inspect the [JSON descriptions](https://github.com/Wasted-Audio/hvcc/tree/develop/hvcc/generators/c2daisy/json2daisy/resources) in the HVCC source repository.

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
| gatein | gate, gate1 | Gate In | gatein_trig |

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
