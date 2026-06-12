import json
import pytest
from rancutils.packet import Packet
from rancutils.neuron import Neuron
from rancutils.core import Core
from rancutils import serialization


def make_neuron(dest_core=None, dest_axon=0, dest_tick=0):
    return Neuron(
        reset_potential=0,
        weights=[1, -1, 1, -1],
        leak=0,
        positive_threshold=2,
        negative_threshold=-2,
        destination_core=dest_core or [0, 0],
        destination_axon=dest_axon,
        destination_tick=dest_tick,
        current_potential=0,
        reset_mode=0,
    )


def make_core(coords=None):
    neurons = [make_neuron() for _ in range(3)]
    connections = [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 0, 0]]
    return Core(
        axons=[0, 1, 0, 1],
        neurons=neurons,
        connections=connections,
        coordinates=coords or [0, 0],
    )


def make_packets():
    return [[
        Packet([0, 0], 0, 0),
        Packet([0, 0], 1, 0),
    ]]


# --- encode / decode roundtrip ---

def test_encode_returns_valid_json():
    cores = [make_core()]
    packets = make_packets()
    output_bus = {'coordinates': [1, 0], 'num_outputs': 3}
    encoded = serialization.encode(cores, packets, output_bus)
    data = json.loads(encoded)
    assert 'cores' in data
    assert 'packets' in data
    assert 'output_bus' in data


def test_encode_decode_packets_roundtrip():
    packets = make_packets()
    cores = [make_core()]
    output_bus = {'coordinates': [1, 0], 'num_outputs': 3}
    encoded = serialization.encode(cores, packets, output_bus)
    data = json.loads(encoded)
    recovered = serialization.parse_packets(data)
    assert recovered is not None
    assert len(recovered) == 1
    assert len(recovered[0]) == 2
    assert recovered[0][0].destination_core == [0, 0]
    assert recovered[0][1].destination_axon == 1


def test_encode_decode_cores_roundtrip():
    cores = [make_core([0, 0]), make_core([1, 0])]
    packets = make_packets()
    output_bus = {'coordinates': [2, 0], 'num_outputs': 3}
    encoded = serialization.encode(cores, packets, output_bus)
    data = json.loads(encoded)
    recovered = serialization.parse_cores(data)
    assert recovered is not None
    assert len(recovered) == 2
    assert recovered[0].coordinates == [0, 0]
    assert recovered[1].coordinates == [1, 0]
    assert len(recovered[0].neurons) == 3


def test_parse_packets_empty():
    assert serialization.parse_packets({}) is None
    assert serialization.parse_packets({'packets': []}) is None


def test_parse_cores_empty():
    assert serialization.parse_cores({}) is None
    assert serialization.parse_cores({'cores': []}) is None


def test_save_and_load(tmp_path):
    cores = [make_core()]
    packets = make_packets()
    output_bus = {'coordinates': [1, 0], 'num_outputs': 3}
    path = str(tmp_path / 'test.json')
    serialization.save(path, cores, packets, output_bus, indent=2)

    recovered_packets, recovered_cores = serialization.load(path)
    assert recovered_packets is not None
    assert recovered_cores is not None
    assert len(recovered_cores) == 1
    assert recovered_cores[0].coordinates == [0, 0]
    assert len(recovered_packets) == 1
    assert len(recovered_packets[0]) == 2


def test_test_json_loads():
    """The simulator's example test.json should parse cleanly."""
    import os
    test_json_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'simulator', 'data', 'test.json'
    ))
    if not os.path.exists(test_json_path):
        pytest.skip('simulator test.json not found')

    recovered_packets, recovered_cores = serialization.load(test_json_path)
    assert recovered_cores is not None
    assert len(recovered_cores) == 1
