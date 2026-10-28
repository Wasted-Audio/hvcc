# ADR-007: MetaModule Generator

Date: 2026-08-19

PR: https://github.com/Wasted-Audio/hvcc/pull/405

## Context

This adds a new generator for the [4ms MetaModule](https://metamodule.info/). It directly implements an MM Native plugin using externed parameters and audio i/o.

## Decision

A new c2meta generator is created that takes a pd project with additional metadata and converts it to a ready to build MetaModule project. Next to the typically required metadata with specific plugin information the user can optionally supply a specific path to the [metamodule-plugin-sdk](https://github.com/4ms/metamodule-plugin-sdk).

The user can also provide specific asset configurations for the panel design and associated Knobs, LEDs and Audio i/o. If the user does not supply such information a panel and parameter/socket layout will be generated automatically based on included default assets. The user can still optionally configure a panel color.

The user needs to at minimum provide the metamodule-plugin-sdk in the output folder, have `cmake` installed on their system and have `arm-none-eabi-gcc` version `15` in their current path.

## MVP Definition

The user should be able to generate a full MetaModule project, build it and run it on their device using just a PD file and optionally some metadata for enhancements.

## Future Improvements

- Allow sliders, switches and encoders
- Send jack connection status to the patch
- Display table contents on the panel
- Somehow build/export multiple modules in a single plugin
