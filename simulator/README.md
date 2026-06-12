# RANC Simulator

A C++ software simulation of the RANC neuromorphic architecture, developed by Dr. Akoglu's Reconfigurable Computing Lab at the University of Arizona.

## Prerequisites

- CMake ≥ 3.10
- C++11-capable compiler (gcc, clang, MSVC)

All other dependencies (RapidJSON, plog, cxxopts) are bundled in `extern/`.

## Building

```bash
mkdir build
cd build
cmake ..
make
```

This produces `build/ranc_sim`.

## Running a Simulation

```
Usage:
  RANCSimulator [OPTION...] INPUT_FILE_NAME, OUTPUT_FILE_NAME, CONFIGURATION_FILE_NAME, NUM_TICKS

  -i, --input arg        Input file
  -o, --output arg       Output file
  -c, --config arg       Config file
      --ticks arg        Number of ticks to run simulation for
  -t, --trace arg        Trace file
  -r, --report_freq arg  Report frequency (default: 1)
  -h, --help             Print help
```

**Minimal example** using the bundled data:

```bash
./build/ranc_sim \
  -i data/example/input.json \
  -o output.txt \
  -c config.json \
  --ticks 10
```

The output file records which neurons spiked on each tick. Ticks where no neurons spike are omitted.

## Input File Format

The input is a JSON file with three top-level keys:

### `packets`
A 2-D array where `packets[i]` contains the packets delivered at tick `i`.

```json
{
  "destination_core": [0, 0],
  "destination_axon": 2,
  "destination_tick": 0
}
```

> **Note:** Packet routing uses absolute `destination_core` coordinates. Neuron output routing uses `destination_core_offset` (relative to the neuron's own core) — see the neuron table below.

### `output_bus`
Specifies which core acts as the output sink and how many output channels it exposes.

```json
{
  "coordinates": [2, 0],
  "num_outputs": 4
}
```

### `cores`
A flat array of core objects. Each core has:

| Field | Description |
|-------|-------------|
| `coordinates` | `[x, y]` grid position |
| `axons` | Array of weight-table indices, one per axon |
| `neurons` | Array of neuron objects (see below) |
| `connections` | 2-D binary crossbar — `connections[i][j]` = 1 means neuron `i` listens to axon `j` |

Each **neuron** object:

| Field | Description |
|-------|-------------|
| `reset_potential` | Value to reset to after a spike |
| `weights` | Array of synaptic weights (indexed by the axon's weight-table entry) |
| `leak` | Subtracted from potential each tick |
| `positive_threshold` | Fire if potential ≥ this value |
| `negative_threshold` | Reset if potential < this value |
| `destination_core_offset` | `[dx, dy]` relative to this core |
| `destination_axon` | Target axon on the destination core |
| `destination_tick` | Tick offset for the outgoing packet |
| `current_potential` | Initial potential |
| `reset_mode` | `0` = absolute reset, `1` = linear reset |

See `data/example/input.json` for a complete annotated example.

## Configuration File

`config.json` sets the grid dimensions and per-component trace verbosity:

```json
{
    "num_neurons": 256,
    "num_axons": 256,
    "num_cores_x": 4,
    "num_cores_y": 3,
    "num_weights": 4,
    "max_tick_offset": 16,
    "neuron_reset_type": 1,
    "neuron_block_trace_verbosity": 0,
    "core_controller_trace_verbosity": 0,
    "scheduler_trace_verbosity": 0
}
```

`neuron_reset_type` controls how the membrane potential is reset after a spike: `0` = absolute reset (potential set to `reset_potential`), `1` = linear reset (potential decremented by threshold).

`num_cores_x * num_cores_y` cores are instantiated. Any core not specified in the input file is initialized with silent neurons (threshold = 1, no connections).

`max_tick_offset` is the depth of the scheduler SRAM. Valid `destination_tick` values are `0` to `max_tick_offset - 1`.

## Trace Files

Pass `-t trace.txt` to write a trace. Verbosity is controlled per-component in `config.json`:

| Parameter | Level | Output |
|-----------|-------|--------|
| `neuron_block_trace_verbosity` | 1 | LIF operation for each neuron each tick |
| | 2 | Level 1 + axons that have both a connection and an incoming spike |
| `core_controller_trace_verbosity` | 1 | Binary spike vector received by each core each tick |
| `scheduler_trace_verbosity` | 1 | Current SRAM word on each update |
| | 2 | Level 1 + every write to the SRAM |

At least one verbosity must be > 0 to use `-t`; specifying `-t` without any verbosity set is an error.

## Simulator Architecture

```
main.cpp
  └─ RANCGrid          — owns the full core grid and drives the tick loop
       └─ Core         — one spiking core
            ├─ Scheduler / SchedulerSRAM  — buffers incoming packets by tick offset
            ├─ CoreController             — dispatches spikes from the scheduler to the neuron block
            ├─ NeuronBlock                — leaky-integrate-and-fire computation
            └─ Router                    — forwards output packets to neighboring cores
```

The `OutputBus` is a special pseudo-core whose spikes are written to the output file instead of being routed further.
