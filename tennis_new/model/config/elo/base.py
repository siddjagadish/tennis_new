from tennis_new.model.config.base import BaseModel
from tennis_new.ml.elo import ELOModel


class ELOBaseModel(BaseModel):

    @property
    def predictor_class(self):
        return ELOModel

    @property
    def predictor_conf(self):
        # To be overwritten
        return {'winner_mod': True}

    @property
    def weighter(self):
        raise NotImplementedError()

    @property
    def winner_id_col(self):
        return 'winner_name'

    @property
    def loser_id_col(self):
        return 'loser_name'

    @property
    def match_id_col(self):
        return 'match_id'

    def fit(self, X, y=None):
        assert self.winner_id_col in X
        assert self.loser_id_col in X
        self.predictor.fit_and_backfill(
            X[self.winner_id_col],
            X[self.loser_id_col],
            X[self.match_id_col],
            ys=None,
            weights=self.weighter.weight(X)
        )

    def update(self, X, y):
        # For now, update just calls fit
        self.fit(X, y)
