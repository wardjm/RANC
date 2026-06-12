# TeaLayers

Custom TensorFlow layers that implement the TeaLearning training methodology for spiking neural networks (SNNs) compatible with constrained neuromorphic architectures such as RANC and IBM TrueNorth.

A **TeaNetwork** is a quantized neural network whose weights map directly to the discrete synaptic weights of a neuromorphic core, making hardware deployment straightforward after training.

Two versions are provided:

| Directory | TensorFlow version |
|-----------|-------------------|
| `tealayer1.0/` | TensorFlow 1.x |
| `tealayer2.0/` | TensorFlow 2.x |

## Installation

```bash
# From the tealayers directory, pick the version matching your TF install:
pip install ./tealayer2.0/   # for TensorFlow 2.x
pip install ./tealayer1.0/   # for TensorFlow 1.x
```

## Layers

| Layer | Description |
|-------|-------------|
| `Tea` | Dense spiking layer with ternary/binary-quantized weights. Maps to one RANC core per unit. |
| `AdditivePooling` | Sums incoming spike counts across an axis; used as the final classification layer. |

## MNIST Example (tealayer2.0)

```python
from tealayer2 import Tea, AdditivePooling
from tensorflow.keras.layers import Flatten, Activation, Input, Lambda, concatenate
from tensorflow.keras.datasets import mnist
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import Model
import numpy as np

(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_train = X_train.astype('float32') / 255
X_test  = X_test.astype('float32')  / 255
y_train = to_categorical(y_train, 10)
y_test  = to_categorical(y_test,  10)

# Tile the 28×28 image across four overlapping 16×16 input cores
inputs           = Input(shape=(28, 28, 1))
flattened_inputs = Flatten()(inputs)
core0 = Lambda(lambda x: x[:, :256])(flattened_inputs)
core1 = Lambda(lambda x: x[:, 176:432])(flattened_inputs)
core2 = Lambda(lambda x: x[:, 352:608])(flattened_inputs)
core3 = Lambda(lambda x: x[:, 528:])(flattened_inputs)

core0 = Tea(units=64, name='tea_1_1')(core0)
core1 = Tea(units=64, name='tea_1_2')(core1)
core2 = Tea(units=64, name='tea_1_3')(core2)
core3 = Tea(units=64, name='tea_1_4')(core3)

network = concatenate([core0, core1, core2, core3])
network = Tea(units=250, name='tea_2')(network)
network = AdditivePooling(10)(network)
predictions = Activation('softmax')(network)

model = Model(inputs=inputs, outputs=predictions)
model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

X_train = X_train.reshape(-1, 28, 28, 1)
X_test  = X_test.reshape(-1,  28, 28, 1)
model.fit(X_train, y_train, batch_size=128, epochs=10, verbose=1, validation_split=0.2)
score = model.evaluate(X_test, y_test, verbose=0)
print("Test accuracy:", score[1])
```

### Exporting to the RANC Simulator

After training, convert the model to a RANC JSON input file and verify it against the simulator:

```python
from rancutils.teaconversion import create_cores, create_packets
from rancutils import OutputBus, save as sim_save
import numpy as np

num_test_samples = 100
x_test_flat = X_test.reshape((len(X_test), 784))

# Absolute (hard) reset — reset_mode 0 in the simulator
cores_sim = create_cores(model, num_tea_layers=2, neuron_reset_type=0)

partitioned_packets = [
    x_test_flat[:num_test_samples, :256],
    x_test_flat[:num_test_samples, 176:432],
    x_test_flat[:num_test_samples, 352:608],
    x_test_flat[:num_test_samples, 528:],
]
packets_sim = create_packets(partitioned_packets)
output_bus_sim = OutputBus((0, 2), num_outputs=250)

sim_save("mnist_config.json", cores_sim, packets_sim, output_bus_sim, indent=2)

# Save TF predictions for cross-validation
test_predictions = model.predict(X_test[:num_test_samples])
np.save("mnist_tf_preds.npy", test_predictions)
np.save("mnist_correct_preds.npy", y_test[:num_test_samples])
```

Run the simulator, then compare outputs:

```python
from rancutils.simulator import collect_classifications_from_simulator

tf_output        = np.argmax(np.load("mnist_tf_preds.npy"), axis=1)
correct_output   = np.argmax(np.load("mnist_correct_preds.npy"), axis=1)
simulator_output = collect_classifications_from_simulator("simulator_output.txt", num_classes=10)

if all(tf_output == simulator_output):
    accuracy = (tf_output == correct_output).mean() * 100
    print(f"Match! Accuracy: {accuracy:.1f}%")
else:
    diff_idx = np.where(tf_output != simulator_output)[0]
    print(f"Differences at indices {diff_idx}")
    print(f"  TF predicted:        {tf_output[diff_idx]}")
    print(f"  Simulator predicted: {simulator_output[diff_idx]}")
    print(f"  Correct labels:      {correct_output[diff_idx]}")
```

A complete interactive walkthrough is available in `tealayer1.0/TeaLearningTutorial/TeaLearning.ipynb`.
