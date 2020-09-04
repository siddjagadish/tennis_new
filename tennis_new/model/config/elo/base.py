from tennis_new.model.config.base import BaseModel
from tennis_new.model.utils.filters import TrainingFilter
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
        return 'p1_link'

    @property
    def loser_id_col(self):
        return 'p2_link'

    @property
    def match_id_col(self):
        return 'match_link'

    @property
    def training_filter(self):
        return TrainingFilter

    def fit(self, X, y=None):
        # TODO: Should make y a property and expect a df instead of X?
        assert self.winner_id_col in X
        assert self.loser_id_col in X
        train_mask = self.training_filter.keep_condition(X)
        self.predictor.fit_and_backfill(
            X[self.winner_id_col],
            X[self.loser_id_col],
            X[self.match_id_col],
            ys=y,
            weights=self.weighter.weight(X),
            filter_mask=train_mask
        )

    def update(self, X, y):
        # For now, update just calls fit
        self.fit(X, y)
