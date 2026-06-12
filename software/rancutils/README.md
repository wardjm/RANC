# RANCUtils

Python utilities for building, serializing, and deploying RANC experiments. It provides the core data model (cores, neurons, packets) and converters that target both the software simulator and the FPGA emulation.

## Installation

```bash
pip install ./software/rancutils/
# or from within the rancutils directory:
pip install .
```

Dependencies: `numpy`, `bitstring`, `imageio`, `pandas`.

## Package Contents

| Module | What it provides |
|--------|-----------------|
| `core.py` | `Core` — holds axons, neurons, connections, and coordinates |
| `neuron.py` | `Neuron` — LIF neuron parameters; `hardware_str()` for FPGA serialization |
| `packet.py` | `Packet` — a single spike packet |
| `output_bus.py` | `OutputBus` — marks the output sink core |
| `serialization.py` | `save` / `load` — read and write the simulator JSON format |
| `emulation.py` | `output_for_streaming` — write CSRAM / TC memory files for FPGA streaming |
| `teaconversion.py` | `create_cores`, `create_packets` — convert a trained TeaLayer model to RANC format |

## Usage

### Building a network manually

```python
from rancutils import Core, Neuron, Packet, OutputBus
from rancutils import save

neuron = Neuron(
    reset_potential=1,
    weights=[1, 1, 1, 1],
    leak=0,
    positive_threshold=1,
    negative_threshold=0,
    destination_core_offset=[1, 0],
    destination_axon=0,
    destination_tick=0,
    current_potential=0,
    reset_mode=1,
)

core = Core(
    axons=[0] * 256,
    neurons=[neuron],
    connections=[[1, 0, 0, 0]],   # neuron 0 listens to axon 0
    coordinates=[0, 0],
)

packets = [[Packet([0, 0], 0, 0)]]
output_bus = OutputBus(coordinates=[1, 0], num_outputs=4)

save("input.json", [core], packets, output_bus, indent=2)
```

### Converting a trained TeaLayer model

```python
from rancutils.teaconversion import create_cores, create_packets
from rancutils import OutputBus, save

# `model` is a compiled Keras model with Tea layers.
cores = create_cores(model, num_tea_layers=2, neuron_reset_type=0)
packets = create_packets(partitioned_input_data)
output_bus = OutputBus([0, 2], num_outputs=250)

save("mnist_config.json", cores, packets, output_bus, indent=2)
```

See [`software/tealayers/README.md`](../tealayers/README.md) for a complete end-to-end MNIST example.

### Generating FPGA emulation files

```python
from rancutils.emulation import output_for_streaming

output_for_streaming(
    cores,
    packets=packets,
    output_path='streaming/',
    verbose=True,
)
```

This writes one `csram_NNN.mem` and one `tc_NNN.mem` per core plus `data.bin` (packets) and `count.bin` (packets per tick) into `streaming/`. Load these into the Vivado project as described in [`hardware/Docs/streaming/streaming.md`](../../hardware/Docs/streaming/streaming.md).

### Loading simulator output

```python
from rancutils.simulator import collect_classifications_from_simulator

results = collect_classifications_from_simulator("output.txt", num_classes=10)
```

## Testing

Unit tests live in `tests/`. They cover `Packet`, `Neuron`, `Core`, and the serialization roundtrip (encode → decode → re-encode).

```bash
pip install pytest
pytest tests/ -v
```

## CSV → JSON Converter

A standalone script at `converter/csv2json.py` converts CSV-formatted core/neuron/packet files into the simulator JSON format. See [`converter/README.md`](converter/README.md) for the full specification and a worked example.
