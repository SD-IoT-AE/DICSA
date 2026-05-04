import numpy as np


class SequenceBuilder:

    def __init__(self, window_size=10):
        self.window_size = window_size

    def build_sequences(self, X, y):
        sequences = []
        labels = []

        for i in range(len(X) - self.window_size):
            seq = X[i:i + self.window_size]
            label = y[i + self.window_size]

            sequences.append(seq)
            labels.append(label)

        return np.array(sequences), np.array(labels)