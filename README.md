# RANC

[![Simulator](https://github.com/UA-RCL/RANC/actions/workflows/simulator.yml/badge.svg)](https://github.com/UA-RCL/RANC/actions/workflows/simulator.yml)
[![rancutils Tests](https://github.com/UA-RCL/RANC/actions/workflows/rancutils_tests.yml/badge.svg)](https://github.com/UA-RCL/RANC/actions/workflows/rancutils_tests.yml)
[![Hardware Unit Tests](https://github.com/UA-RCL/RANC/actions/workflows/hardware_unit_tests.yml/badge.svg)](https://github.com/UA-RCL/RANC/actions/workflows/hardware_unit_tests.yml)

RANC (Reconfigurable Architecture for Neuromorphic Computing) is a full-featured environment for experimentation with neuromorphic architectures developed by Dr. Akoglu's Reconfigurable Computing Lab at the University of Arizona. See https://ua-rcl.github.io/projects/ranc for more details.

## Architecture Overview

RANC models a grid of spiking neuron cores. Each core contains a synaptic crossbar, a scheduler SRAM, and a leaky-integrate-and-fire neuron block. Cores communicate by routing spike packets through an on-chip network. The same architecture is available as a software simulator (for development and verification) and as an FPGA IP core (for emulation at hardware speeds).

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Training (Python / TensorFlow)                              │
  │   tealayers ──► rancutils ──► JSON input file                │
  └──────────────────────────┬───────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
  ┌─────────────────────┐       ┌─────────────────────────────┐
  │  C++ Simulator      │       │  FPGA Emulation (Vivado)    │
  │  simulator/         │       │  hardware/                  │
  │  ranc_sim -i ...    │       │  + streaming via DMA        │
  └─────────────────────┘       └─────────────────────────────┘
```

## Sub-projects

| Directory | Description |
|-----------|-------------|
| [`simulator/`](simulator/) | C++ software simulator — build and run RANC experiments without hardware |
| [`hardware/`](hardware/) | Vivado FPGA project — RANC IP core and streaming project for Xilinx Zynq UltraScale+ |
| [`software/`](software/) | Python utilities for preparing inputs, training networks, and processing outputs |
| [`experiments/`](experiments/) | Self-contained example experiments (EEG classification, VMM) |

## Typical Workflow

1. **Train** a spiking neural network with [`software/tealayers`](software/tealayers/) inside TensorFlow.
2. **Convert** the trained model to a RANC input JSON using [`software/rancutils`](software/rancutils/).
3. **Simulate** with the [`simulator`](simulator/) to verify correctness.
4. **Deploy** to the FPGA emulation using `rancutils.emulation.output_for_streaming` to generate the memory files, then stream data via the Xilinx SDK (see [`hardware/Docs/streaming/`](hardware/Docs/streaming/)).

## Dependencies

| Component | Requirements |
|-----------|-------------|
| Simulator | CMake ≥ 3.10, C++11 compiler (gcc/clang) |
| Software (rancutils, tealayers, vmmmap) | Python 3, TensorFlow (for tealayers), numpy, bitstring, pandas |
| Hardware | Xilinx Vivado 2018.2+, Zynq UltraScale+ board |

## Quick Start

```bash
# 1. Build the simulator
cd simulator
mkdir build && cd build
cmake .. && make
cd ../..

# 2. Install Python utilities
pip install ./software/rancutils/
pip install ./software/tealayers/tealayer2.0/  # for TF2

# 3. Run the bundled example
cd simulator
./build/ranc_sim -i data/example/input.json -o output.txt -c config.json --ticks 10
```

## Citation

If you use RANC in your research, please cite using the information in [`CITATION.cff`](CITATION.cff).
