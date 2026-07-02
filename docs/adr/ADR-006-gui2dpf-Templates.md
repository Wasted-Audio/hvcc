# ADR-006: gui2dpf Templates

Date: 2026-05-13
Issue: https://github.com/Wasted-Audio/hvcc/issues/296

## Context

A new [PDVG](https://github.com/Wasted-Audio/PDVG) widget library for DPF was created, which implements Plugdata GUI objects using NanoVG.

We can now use this widget library in combination with the GUI JSON, created by the pd2gui stage in hvcc, to generate an emulated UI for the DPF generator.

## Decision

We create a new c2dpf code-path, with a set of templates, to combine the GUI JSON with the new widget library.

In order to have backwards compatibility with the previous ImGui UI implementation we introduce a new `DPFUIType` in the meta JSON. This allows to keep the old boolean behavior, which selects ImGui as the GUI type, but allows to extend it using integer enumeration. This could allow for other UI extensions in the future as well.

We add the ability to create `@hv_event` based parameters to allow for the same behavior as `[bang]` object. This brings DPF on par with Unity and Javascript implementations.

The GUI JSON will need some minor modifications to better align to the PDVG requirements.

## MVP Definition

The user should be able to generate a GUI for their DPF plugins that matches the basic Plugdata UI as close as possible.

## Future Improvements

More GUI objects and better object behavior may be added in the future. More accuracy in the layout and design may also be required.
