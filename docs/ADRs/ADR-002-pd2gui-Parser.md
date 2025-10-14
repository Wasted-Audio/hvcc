# ADR-001: pd2gui Parser

Date: 2025-09-12

Issue: https://github.com/Wasted-Audio/hvcc/issues/294

## Context

The Heavy Compiler currently focusses on compiling PD patches on the DSP and Control level. PD however is a graphical environment and users will often use the GUI elements to design interfaces for controlling their patches. Therefore it is proposed to be able to use these GUI objects to design control interfaces. The goal is to create a PD patch parser that only takes into account visible GUI objects, that are connected to externed Heavy parameters, and generates an intermediate JSON object that can then be used downstream to create various new control interfaces.

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

### Object settings

Not all GUI objects are equal and they support a variety of options:

- `position`: x/y coordinates, supported by all
- `label`: which has `text`, `color`, `position` (x/y), and `height` [bng, tgl, vradio, hradio, vsl, nbx, hsl, cnv]
- `label`: with only `text` and `position` (left/right/top/bottom) [floatatom]
- `label`: with `size`, `position` (x/y), `show number` (never/always/when active/when typing) [knob]
- `size`: single value [bng, tgl, vradio, hradio, knob]
- `size`: x/y [vsl, hsl, canvas]
- `size`: width (chars) [nbx]
- `size`: width/font height [floatatom]
- `minimum`: value [vsl, hsl, knob, floatatom]
- `maximum`: value [vsl, hsl, knob, floatatom]
- `foreground`: color [bng, tgl, vsl, hsl, vradio, hradio, nbx, knob]
- `background`: color [bng, tgl, vsl, hsl, vradio, hradio, nbx, knob, canvas]
- `options`: integer amount [vradio, hradio]
- `initialize`: [bng, tgl, nbx, vradio, hradio, vsl, hsl, canvas]
- `min/max flash time`: integers [bng]
- `non-zero value`: float [tgl]
- `logarithmic`: bool [vsl, hsl]
- `steady`: steady on click / jump on click [vsl, hsl]

Unique to [knob]:

- `initial value`: float
- `angular range`: int
- `angular offset`: int
- `arc start`: float
- `log mode`: linear/logarithmic/exponential
- `exp factor`: float
- `discrete`: bool
- `show ticks`: bool
- `steps`: int (number of ticks)
- `circular drag`: bool
- `read only`: bool
- `jump on click`: bool
- `variable`
- `parameter`
- `arc`: color
- `square`: bool
- `show arc`: bool

The location of these settings in the object line in the pd patch will be different depending on the object type.

The canvas of the main patch, subpatches and abstractions has the following properties:

- `position`: x/y coordinates - position in the host patch (not needed for the top level)
- `width`: int
- `height`: int
- `graph on parent`: bool - required for subpatches and abstractions, otherwise the entire object is ignored
- `hide name and args`: bool - not particularly useful, but maybe needed for consistency
- `x range`: float, float - segment of the graph that is exposed to parent
- `y range`: float, float - segment of the graph that is exposed to parent

The order of objects determines the order in which they are displayed. First in the patch file means displayed on top.

It might not be feasible, or sensible, to include all of the available object settings.

## Decision

A new parser will be created, using a similar approach to pd2hv. The parser selects valid GUI objects containing `@hv_param` receive configurations and constructs validated pydantic objects that are added to a GUI-graph definition. Subpatches and abstractions that have graph-on-parent enabled will be recursively parsed as well, thus expanding the graph.

### Intermediate JSON

Each of the parsed objects should be validated through a pydantic object and the final intermediate result JSON will then consist of a list of objects and a number of general settings. Because there can be nested objects, part of the JSON is recursive where each graph can contain a number of sub-graphs.

### Object Visibility

Only GUI objects that fit within the visible canvas should be added. This means that their position and size should be compared to the current canvas width and height. It will need to be determined if objects are allowed to be cut-off, or if they need to entirely fit within the current view.

### Parser

The high level structure of the parser can be based on the current pd2hv interpreter. With a main `PdParser` construct that can parse graphs from files and canvas. However instead of PdGraph objects it could construct the intermediate GUI JSON file, based on the pydantic object definitions, directly. The JSON can then be stored as `<name>.gui.ir.json` in the `ir` output folder.

## MVP Definition

Being able to recursively parse a PD patch based on exposed GUI objects and generating an intermediate JSON that can be used in subsequent steps for creating custom UIs. The JSON configuration should contain most, of not all, of the GUI object settings so that consistent behavior emulation can be created.

## Future Improvements

Be able to run the pd2gui step independently from the DSP parser.
