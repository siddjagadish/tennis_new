import pandas as pd
from tennis_new.model.config.base import BaseModel
from tennis_new.model.utils.filters import (
    Filter,
    DateFilter,
    TrainingFilter
)
from tennis_new.model.utils.evaluation import BasicEvaluator
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

    @property
    def test_filter(self):
        class MyTestFilter(Filter):
            sub_filters = [
                self.training_filter,
                DateFilter(min_date='2011-01-01', max_date='2015-01-01')
            ]
        return MyTestFilter

    @property
    def baseline_pred_col(self):
        return 'odds_implied_probability'

    @property
    def evaluator(self):
        # return BasicEvaluator('prediction', self.baseline_pred_col)  # TODO: Reinclude this
        return BasicEvaluator('prediction')

    def fit(self, X, y=None):
        # TODO: Should make y a property and expect a df instead of X?
        assert self.winner_id_col in X
        assert self.loser_id_col in X
        train_mask = self.training_filter.keep_condition(X)
        self.history_df = self.predictor.fit_and_backfill(
            X[self.winner_id_col],
            X[self.loser_id_col],
            X[self.match_id_col],
            ys=y,
            weights=self.weighter.weight(X),
            filter_mask=train_mask
        )

    def run(self, X, y=None):
        self.fit(X, y=None)
        test_set = self.test_filter.filter_data(X)
        for_eval_df = pd.merge(
            test_set,
            self.history_df,
            left_on=self.match_id_col,
            right_on='match_id'  # TODO: Make fit_and_backfill use self.match_id_col?
        )
        assert for_eval_df.shape[0] == test_set.shape[0]
        self.evaluation = self.evaluator.evaluate(for_eval_df)

    def update(self, X, y):
        # For now, update just calls fit
        self.fit(X, y)
