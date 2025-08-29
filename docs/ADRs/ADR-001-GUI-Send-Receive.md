# ADR-001: GUI Send Receive

Date: 2025-08-29
Issue: https://github.com/Wasted-Audio/hvcc/issues/186

## Context

In PD each UI object can have integrated send and receive configurations. In Heavy we replace the UI objects with a float object so any such configurations are lost after conversion. It would be nice if the user can use these configurations and make use of this PD functionality in the converted code.

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
- Symbol atom (symbolatom)

There are some objects that also have send/receive capabilities, but at this moment it doesn't make sense to support them:

- Canvas (cnv)

## Decision

We can take a similar approach as the remote message functionality where we parse the objects, register send/receive objects in a dictionary with the connecting object id as the key. Then at the end of the graph parsing we create the send/receive objects and associated connections. Thus artificially extending the graph with the missing objects.

There are some complicating factors. Not each object stores its configuration in the same location so this needs additional adjustments. Also because the objects are serialized on a single line any send/receive configuration that has spaces in it is escaped with a backslash. Therefore we need to account for this when splitting the configuration arguments, which is currently not the case. Any escaped names should then be sanitized in order to pass them correctly.

Instead of a plain float box we then end up with an extended graph with additional send/receive objects:

```
[receive recv_name]
|
[f ]
|
[send send_name]
```

## MVP Definition

Be able to set send and/or receive configuration on PD GUI objects and be able to use the same identifiers to receive/send to these in the patch. This configuration should also support spaces in the identifiers. Because we also use send/receive objects for externalizing parameters this should be able to work here as well.

## Future Improvements

This should have little to no impact on other existing functionality and only adds a new feature.

When we work on the pd2gui parser these send/receive configurations can be re-used to identify externalized parameters and their association to graphical objects.
