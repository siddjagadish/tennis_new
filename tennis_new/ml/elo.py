import numpy as np
import pandas as pd
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

    def update(self, p1_id, p2_id, y1, y2, weight=1., match_id=None, use_for_update=1):
        # y1 is # of times in a match (sets, games, etc.) p1 beat p2; y2 is the opposite.
        pred = self.predict(p1_id, p2_id)
        old_beta1 = self.beta[p1_id]
        old_beta2 = self.beta[p2_id]

        if use_for_update == 1:
            # Learning Rates
            lr1 = weight * self.c / ((self.match_counts[p1_id] + self.o) ** self.s)
            lr2 = weight * self.c / ((self.match_counts[p2_id] + self.o) ** self.s)

            p1_win_update = 1. - pred
            p2_win_update = pred
            p1_lose_update = -pred
            p2_lose_update = pred - 1.

            beta1_total_update = p1_win_update * y1 + p1_lose_update * y2
            beta2_total_update = p2_win_update * y2 + p2_lose_update * y1
            new_beta1 = self.beta[p1_id] + lr1 * beta1_total_update
            new_beta2 = self.beta[p2_id] + lr2 * beta2_total_update

            self.beta[p1_id] = new_beta1
            self.beta[p2_id] = new_beta2

            n_obs = int(y1 + y2)
            self.match_counts[p1_id] += n_obs
            self.match_counts[p2_id] += n_obs

        return {
            'match_id': match_id,
            'prediction': pred,
            'p1_id': p1_id,
            'p2_id': p2_id,
            'elo1': old_beta1,
            'elo2': old_beta2,
        }

    def fit_and_backfill(self, p1_ids, p2_ids, match_ids, ys=None, weights=None, filter_mask=None):
        assert len(p1_ids) == len(p2_ids) == len(match_ids)

        if filter_mask is None:
            filter_mask = np.ones(len(p1_ids)).astype(int)
        else:
            filter_mask = filter_mask.astype(int)

        if ys is None:
            if not self.winner_mod:
                raise ValueError(
                    "Must specify that this is a 'winner mod' (1st index is always winner) or must supply y values"
                )
            y1s = np.ones(len(p1_ids)).astype(int).tolist()
            y2s = np.zeros(len(p1_ids)).astype(int).tolist()
        elif ys.shape[1] > 1:  # If set model
            ys = ys.astype(int)
            y1s = ys[:, 0]
            y2s = ys[:, 1]
        else:
            raise ValueError("ELO Class Only Equipped to Handle Array-valued ys.  Otherwise, use winner_mod=True")

        if weights is None:
            weights = np.ones(len(p1_ids)).tolist()

        for p1_id, p2_id, y1, y2, w, match_id, fm in zip(
                p1_ids,
                p2_ids,
                y1s,
                y2s,
                weights,
                match_ids,
                filter_mask
        ):
            self.history.append(
                self.update(p1_id, p2_id, y1, y2, weight=w, match_id=match_id, use_for_update=fm)
            )
        return pd.DataFrame(self.history)

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

