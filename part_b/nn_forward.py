import os
import gzip
import numpy as np


def one_hot_encoding(labels, dimension=10):
    one_hot_labels = labels[..., None] == np.arange(dimension)[None]
    return one_hot_labels.astype(np.float64)


def load_data(test_sample=1000):
    data_dir = "mnist"
    with gzip.open(os.path.join(data_dir, "t10k-images-idx3-ubyte.gz"), "rb") as mnist_file:
        x_test = np.frombuffer(mnist_file.read(), np.uint8, offset=16).reshape(-1, 28 * 28)
    test_images = x_test[0:test_sample] / 255
    return test_images


def load_label(test_sample=1000):
    data_dir = "mnist"
    with gzip.open(os.path.join(data_dir, "t10k-labels-idx1-ubyte.gz"), "rb") as mnist_file:
        y_test = np.frombuffer(mnist_file.read(), np.uint8, offset=8)
    test_labels = one_hot_encoding(y_test[:test_sample])
    return test_labels


# @profile
# def layer1(x):
#     weights_1 = np.load("w1.npy")
#     x = x @ weights_1
#     return (x >= 0) * x
#
# @profile
# def layer2(x):
#     weights_2 = np.load("w2.npy")
#     x = x @ weights_2
#     return np.argmax(x, axis=1)
#
# @profile
# def main():
#     test_sample = 10
#     test_images, test_labels = load_data(test_sample)
#
#     # Inference
#     x = layer1(test_images)
#     x = layer2(x)
#
#     accuracy = np.sum(x == np.argmax(test_labels, axis=1))
#     print(accuracy / test_sample)

@profile
def main():
    test_sample = 100
    test_images = load_data(test_sample)

    # layer1
    weights_1 = np.load("w1.npy")
    x = test_images @ weights_1
    x = (x >= 0) * x

    # layer2
    weights_2 = np.load("w2.npy")
    x = x @ weights_2
    x = (x >= 0) * x

    # layer3
    weights_3 = np.load("w3.npy")
    x = x @ weights_3
    x = np.argmax(x, axis=1)

    test_labels = load_label(test_sample)
    accuracy = np.sum(x == np.argmax(test_labels, axis=1))
    print(accuracy / test_sample)


if __name__ == '__main__':
    main()
