import os
import gzip
import numpy as np


def one_hot_encoding(labels, dimension=10):
    one_hot_labels = labels[..., None] == np.arange(dimension)[None]
    return one_hot_labels.astype(np.float64)


def relu(x):
    return (x >= 0) * x


def relu2deriv(output):
    return output >= 0


@profile
def main():
    data_sources = {"training_images": "train-images-idx3-ubyte.gz", "test_images": "t10k-images-idx3-ubyte.gz", "training_labels": "train-labels-idx1-ubyte.gz", "test_labels": "t10k-labels-idx1-ubyte.gz"}

    data_dir = "mnist"
    mnist_dataset = {}

    for key in ("training_images", "test_images"):
        with gzip.open(os.path.join(data_dir, data_sources[key]), "rb") as mnist_file:
            mnist_dataset[key] = np.frombuffer(mnist_file.read(), np.uint8, offset=16).reshape(-1, 28 * 28)

    for key in ("training_labels", "test_labels"):
        with gzip.open(os.path.join(data_dir, data_sources[key]), "rb") as mnist_file:
            mnist_dataset[key] = np.frombuffer(mnist_file.read(), np.uint8, offset=8)

    x_train, y_train, x_test, y_test = (mnist_dataset["training_images"], mnist_dataset["training_labels"], mnist_dataset["test_images"], mnist_dataset["test_labels"])

    training_sample, test_sample = 1000, 1000
    training_images = x_train[0:training_sample] / 255
    test_images = x_test[0:test_sample] / 255
    training_labels = one_hot_encoding(y_train[:training_sample])
    test_labels = one_hot_encoding(y_test[:test_sample])

    seed = 884736743
    rng = np.random.default_rng(seed)

    learning_rate = 0.005
    epochs = 10
    hidden_size = 100
    pixels_per_image = 784
    num_labels = 10

    weights_1 = 0.2 * rng.random((pixels_per_image, hidden_size)) - 0.1
    weights_2 = 0.2 * rng.random((hidden_size, num_labels)) - 0.1

    store_training_loss = []
    store_training_accurate_pred = []
    store_test_loss = []
    store_test_accurate_pred = []

    for j in range(epochs):

        training_loss = 0.0
        training_accurate_predictions = 0

        for i in range(len(training_images)):
            layer_0 = training_images[i]

            layer_1 = np.dot(layer_0, weights_1)

            layer_1 = relu(layer_1)

            dropout_mask = rng.integers(low=0, high=2, size=layer_1.shape)

            layer_1 *= dropout_mask * 2

            layer_2 = np.dot(layer_1, weights_2)

            training_loss += np.sum((training_labels[i] - layer_2) ** 2)

            training_accurate_predictions += int(np.argmax(layer_2) == np.argmax(training_labels[i]))

            layer_2_delta = training_labels[i] - layer_2

            layer_1_delta = np.dot(weights_2, layer_2_delta) * relu2deriv(layer_1)

            layer_1_delta *= dropout_mask

            weights_1 += learning_rate * np.outer(layer_0, layer_1_delta)
            weights_2 += learning_rate * np.outer(layer_1, layer_2_delta)

        store_training_loss.append(training_loss)
        store_training_accurate_pred.append(training_accurate_predictions)

        results = relu(test_images @ weights_1) @ weights_2

        test_loss = np.sum((test_labels - results) ** 2)

        test_accurate_predictions = np.sum(np.argmax(results, axis=1) == np.argmax(test_labels, axis=1))

        store_test_loss.append(test_loss)
        store_test_accurate_pred.append(test_accurate_predictions)


if __name__ == '__main__':
    main()
