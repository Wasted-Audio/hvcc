Current oneliner to run recpatch.pd

`pd -blocksize 512 -rt -noaudio -r 48000 -nogui -open recpatch.pd -send "recsave symbol test-phasor-control-rec.golden.wav" -send "recpatch symbol test-phasor-control-rec.pd"`
