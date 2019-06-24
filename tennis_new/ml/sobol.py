# Implements Sobol Sampling
import numpy as np
from sobol import i4_sobol


def generate_sobol_seq(dim, n, seed):
    seed = seed
    out = []
    for i in range(n):
        cur_out, seed = i4_sobol(dim, seed)
        out.append(cur_out)
    return np.array(out)


def _check_randos(rs):
    assert all(0. <= x <= 1. for x in rs)


def get_range_values(mini, maxi, randos):
    '''
    :param mini: float/int minimum of param value
    :param maxi: float/int maximum of param value
    :param randos: iterable of random floats between 0 and 1
    :return: list of parameter values
    '''
    _check_randos(randos)
    return np.array(
        list(map(lambda x: x * (maxi - mini) + mini, randos))
    )
