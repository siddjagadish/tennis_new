import numpy as np
from collections import defaultdict


class GlickoModel(object):
    # TODO: Finish this class
    # TODO: Refactor so that Glicko and ELO use same parent class
    Q = np.log(10) / 400
    DEFAULT_GLICKO_RATING = 1500
    DEFAULT_GLICKO_RD = 350

    def __init__(self, ratings=None, rds=None, c=63.2):
        if self.ratings is None:
            ratings = {}
        self.ratings = defaultdict(lambda x: self.DEFAULT_GLICKO_RATING, ratings)
        if self.rds is None:
            self.rds = {}
        self.rds = defaultdict(lambda x: self.DEFAULT_GLICKO_RD, rds)
        self.c = c

    @classmethod
    def g(cls, rd):
        denom = 1. + 3 * (cls.Q ** 2) * (rd ** 2) / np.pi
        return 1. / denom

    @staticmethod
    def _predict(cur_g, rating_i, rating_j):
        return 1. / (1. + 10. ** (cur_g * (rating_i - rating_j) / 400))

    @classmethod
    def player_expected_outcome(cls, g_j, rating_i, rating_j, rd_j):
        return cls._predict(g_j, rating_i, rating_j)

