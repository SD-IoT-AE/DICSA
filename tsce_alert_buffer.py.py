from collections import deque
import numpy as np


class AlertBuffer:

    def __init__(self, window_size=10):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def add(self, feature_vector):
        self.buffer.append(feature_vector)

    def is_ready(self):
        return len(self.buffer) == self.window_size

    def get_sequence(self):
        return np.array(self.buffer)

    def reset(self):
        self.buffer.clear()