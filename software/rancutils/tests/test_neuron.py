import pytest
from rancutils.neuron import Neuron


def make_neuron(**kwargs):
    defaults = dict(
        reset_potential=0,
        weights=[1, -1, 1, -1],
        leak=0,
        positive_threshold=2,
        negative_threshold=-2,
        destination_core=[0, 0],
        destination_axon=0,
        destination_tick=0,
        current_potential=0,
        reset_mode=0,
    )
    defaults.update(kwargs)
    return Neuron(**defaults)


def test_neuron_creation():
    n = make_neuron()
    assert n.reset_potential == 0
    assert n.weights == [1, -1, 1, -1]
    assert n.destination_core_offset == [0, 0]


def test_neuron_requires_2d_core():
    with pytest.raises(AssertionError):
        make_neuron(destination_core=[0])


def test_hardware_str_is_binary():
    n = make_neuron()
    s = n.hardware_str()
    assert all(c in '01' for c in s)
    assert len(s) > 0


def test_hardware_str_length():
    n = make_neuron()
    s = n.hardware_str(
        potential_width=9,
        leak_width=9,
        weight_width=9,
        threshold_width=9,
        num_reset_modes=2,
        max_dx=512,
        max_dy=512,
        num_axons=256,
        num_ticks=16,
    )
    # current_potential(9) + reset_potential(9) + weights(9*4=36) + leak(9)
    # + pos_thresh(9) + neg_thresh(9) + reset_mode(1) = 82 neuron params
    # dx(9) + dy(9) + axon(8) + tick(4) = 30 spike dest
    # total = 112
    assert len(s) == 112


def test_hardware_str_zero_neuron():
    n = make_neuron(weights=[0, 0, 0, 0])
    s = n.hardware_str(
        potential_width=9,
        leak_width=9,
        weight_width=9,
        threshold_width=9,
        num_reset_modes=2,
        max_dx=512,
        max_dy=512,
        num_axons=256,
        num_ticks=16,
    )
    # positive_threshold=2 so not all zeros, but structure should be valid
    assert len(s) == 112
    assert all(c in '01' for c in s)
