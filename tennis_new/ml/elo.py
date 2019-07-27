# Old Elo Class -- try with labels always 1
import json
import numpy as np
from collections import defaultdict


class ELOModel(object):
    DEFAULT_ELO_RATING = 1500

    def __init__(self, c=250., o=5., s=0.4, match_counts=None, beta=None, winner_mod=False):
        self.c = c
        self.o = o
        self.s = s

        if match_counts is None:
            match_counts = {}
        self.match_counts = defaultdict(lambda: 0, match_counts)

        # beta stores player ELO ratings
        if beta is None:
            beta = {}
        self.beta = defaultdict(lambda: self.DEFAULT_ELO_RATING, beta)

        self.winner_mod = winner_mod
        self.history = []

    @staticmethod
    def elo(x):
        # Just a rescaled sigmoid
        return 1. / (1. + 10. ** (-x / 400.))

    def update(self, p1_id, p2_id, y, weight=1., match_id=None):
        pred = self.predict(p1_id, p2_id)

        lr1 = weight * self.c / ((self.match_counts[p1_id] + self.o) ** self.s)
        lr2 = weight * self.c / ((self.match_counts[p2_id] + self.o) ** self.s)

        old_beta1 = self.beta[p1_id]
        old_beta2 = self.beta[p2_id]

        new_beta1 = self.beta[p1_id] + lr1 * (y - pred)
        new_beta2 = self.beta[p2_id] + lr2 * (pred - y)

        self.beta[p1_id] = new_beta1
        self.beta[p2_id] = new_beta2

        self.match_counts[p1_id] += 1
        self.match_counts[p2_id] += 1

        return {
            'match_id': match_id,
            'p1_id': p1_id,
            'p2_id': p2_id,
            'elo1': old_beta1,
            'elo2': old_beta2,
            'elo_match_prediction': pred
        }

    def fit_and_backfill(self, p1_ids, p2_ids, match_ids, ys=None, weights=None):
        if ys is None:
            if not self.winner_mod:
                raise ValueError(
                    "Must specify that this is a 'winner mod' (1st index is always winner) or must supply y values"
                )
            ys = np.ones(len(p1_ids)).tolist()
        if weights is None:
            weights = np.ones(len(p1_ids)).tolist()
        for p1_id, p2_id, y, w, match_id in zip(
                p1_ids,
                p2_ids,
                ys,
                weights,
                match_ids
        ):
            self.history.append(
                self.update(p1_id, p2_id, y, weight=w, match_id=match_id)
            )

    def predict(self, p1_id, p2_id):
        return self.elo(self.beta[p1_id] - self.beta[p2_id])

    def state_to_dict(self):
        return {
            'beta': self.beta,
            'match_counts': self.match_counts,
            'c': self.c,
            'o': self.o,
            's': self.s,
            'winner_mod': self.winner_mod
        }