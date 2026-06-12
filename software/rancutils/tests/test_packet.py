import pytest
from rancutils.packet import Packet


def test_packet_creation():
    p = Packet([0, 0], 3, 1)
    assert p.destination_core == [0, 0]
    assert p.destination_axon == 3
    assert p.destination_tick == 1


def test_packet_requires_2d_core():
    with pytest.raises(AssertionError):
        Packet([0], 0, 0)


def test_hardware_str_length():
    p = Packet([0, 0], 0, 0)
    s = p.hardware_str(max_dx=512, max_dy=512, num_axons=256, num_ticks=16)
    # dx: 9 bits, dy: 9 bits, axon: 8 bits, tick: 4 bits = 30 bits
    assert len(s) == 30
    assert all(c in '01' for c in s)


def test_hardware_str_values():
    p = Packet([1, 2], 5, 3)
    s = p.hardware_str(max_dx=512, max_dy=512, num_axons=256, num_ticks=16)
    assert len(s) == 30
    # Spot-check: should be non-zero since coords/axon/tick are non-zero
    assert '1' in s


def test_hardware_str_zero():
    p = Packet([0, 0], 0, 0)
    s = p.hardware_str(max_dx=512, max_dy=512, num_axons=256, num_ticks=16)
    assert s == '0' * 30
