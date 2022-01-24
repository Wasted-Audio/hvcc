# Distrho Plugin Format Generator example help

To build the sample run hvcc with the DPF generator and metadata option on an output directory:

```bash
$ mkdir dpf_example
$ hvcc dpf_example.pd -o dpf_example/ -g dpf -n dpf_example -m dpf_example.json
$ cd dpf_example/
$ git clone https://github.com/DISTRHO/DPF.git dpf
$ make
```

The binaries will be in `bin/`