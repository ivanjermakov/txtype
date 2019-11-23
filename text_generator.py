import numpy as np


def generate(dictionary_path, length):
    words = [line.rstrip('\n') for line in open(dictionary_path)]
    return np.random.choice(words, length, replace=False).tolist()
