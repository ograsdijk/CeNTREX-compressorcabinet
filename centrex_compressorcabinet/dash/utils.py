import numpy as np


def moving_average(array, averaging):
    return np.convolve(array, np.ones(averaging), "valid") / averaging
