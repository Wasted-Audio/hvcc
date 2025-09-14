# ADR-001: pd2gui Parser

Date: 2025-09-12
Issue: https://github.com/Wasted-Audio/hvcc/issues/294

## Context

The Heavy Compiler currently focusses on compiling PD patches on the DSP and Control level. PD however is a graphical environment and users will often use the GUI elements to design interfaces for controlling their patches. Therefore it is proposed to be able to use these GUI objects to design control interfaces. The goal is to create a PD patch parser that only takes into account visible GUI objects, that are connected to externed Heavy parameters, and generates an intermediate json object that can then be used downstream to create various new control interfaces.

Possible objects to include:

- Number box (nbx)
- Vertical slider (vsl)
- Horizontal slider (hsl)
- Vertical radio buttons (vradio)
- Horizontal radio buttons (hradio)
- Bang (bng)
- Toggle (tgl)
- Knob (knob, else/knob)
- Float atom (floatatom)
- Canvas (cnv)
- Comment (text)

## Decision

## MVP Definition

## Future Improvements
