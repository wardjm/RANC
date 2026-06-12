# Hardware Documentation

Documentation for deploying RANC on FPGA hardware.

## Contents

### [streaming/streaming.md](streaming/streaming.md)

Step-by-step tutorial for setting up a full streaming environment on a Xilinx Zynq UltraScale+ board. Covers:

- Assembling the Vivado block design (MPSoC, AXI DMA, Tick Generator, RANC IP, AXI-Stream Packet Buffer)
- Exporting the bitstream and launching the Xilinx SDK
- Writing the bare-metal C applications (`streamingtx.c` / `streamingrx.c`) that move data between the ARM cores and the FPGA
- Loading MNIST data from an SD card and streaming classifications back to the terminal

The `streaming/data/` directory contains the pre-generated CSRAM / TC memory files and packet binaries for a 5-core MNIST network used in that tutorial.

## Related

- [`hardware/IP/RANCNetwork/`](../IP/RANCNetwork/) — RANC network IP source and Vivado project script
- [`hardware/Projects/Streaming/`](../Projects/Streaming/) — pre-built streaming block design
- [`software/rancutils/`](../../software/rancutils/) — Python tools for generating the memory files loaded by the hardware
