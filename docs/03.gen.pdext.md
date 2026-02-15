# Pdext

Pure Data externals allow you to reuse compiled Heavy code in subsequent Pd patches. Because of how Heavy runs its process we will always create a signal object that only runs with DSP turned on (although it is possible to only have control i/o). Therefore the created external will always have the signal `~` appended after the name.

The external will always have one inlet and one outlet for control messages. With one or more signal inlets the first inlet will be shared for signal and control connections. Signal outlets are separate from the right-most control outlet.

## Receivers and Senders

Using named receivers, ie. `[r foo @hv_param]`, it is possible to send `bang`, `symbol`, `float`, and a list of `atoms` (more than 2 elements) messages by starting your message with the intended name, `[foo $1(`. These can only be attached to the first inlet of the external.

All outgoing control messages must be passed to a send object with the name `[s HV_TO_PD @hv_param]`. If your outgoing message is more than 2 atoms and starts with a `symbol` it will output as a `list` object. If it starts with a float it is a regular multi atom message. All other single atom values will output as their corresponding types respectively.

## Print Hook

It is possible to directly print to the console of pd from inside the external. The print hook is prepended with the external name and a timestamp in ms since the start of the external object: `[printtest~ @ 500ms] print: something`.
