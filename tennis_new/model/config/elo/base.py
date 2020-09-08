import numpy as np
import pandas as pd
from tennis_new.model.config.base import BaseModel
from tennis_new.model.base import DummyWeighter
from tennis_new.model.utils.filters import (
    Filter,
    DateFilter,
    TrainingFilter,
    MissingScoreFilter,
    MissingPIDFilter
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
        return DummyWeighter()

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
    def date_col(self):
        return 'date'

    @property
    def training_filter(self):
        return TrainingFilter()

    @property
    def validation_filter(self):
        class MyValidationFilter(Filter):
            sub_filters = [
                MissingPIDFilter(),
                MissingScoreFilter(),
                DateFilter(min_date='2011-01-01', max_date='2015-01-01')
            ]
        return MyValidationFilter()

    @property
    def test_filter(self):
        class MyTestFilter(Filter):
            sub_filters = TrainingFilter.sub_filters + [
                MissingPIDFilter(),
                MissingScoreFilter(),
                DateFilter(min_date='2015-01-01', max_date='2021-01-01')
            ]
        return MyTestFilter()

    @property
    def baseline_pred_col(self):
        return 'odds_implied_probability'

    @property
    def evaluator(self):
        return BasicEvaluator('prediction', self.baseline_pred_col)

    def post_process(self):
        # Any post-processing steps for the predictions
        pass

    def fit(self, df):
        # TODO: Should make y a property and expect a df instead of X?
        assert self.winner_id_col in df
        assert self.loser_id_col in df
        # Assert df is sorted
        assert np.array_equal(df[self.date_col].values, df[self.date_col].sort_values(ascending=True).values)
        train_mask = self.training_filter.keep_condition(df)
        if self.y is not None:
            ys = df[self.y].values
        else:
            ys = None
        self.history_df = self.predictor.fit_and_backfill(
            df[self.winner_id_col],
            df[self.loser_id_col],
            df[self.match_id_col],
            ys=ys,
            weights=self.weighter.weight(df),
            filter_mask=train_mask
        )
        self.all_jd = pd.merge(
            df,
            self.history_df,
            left_on=self.match_id_col,
            right_on='match_id',
            how='left'
        )

    def _run_evaluation(self, data_filter):
        for_eval_df = data_filter.filter_data(self.all_jd)
        if not for_eval_df[self.match_id_col].isin(self.history_df['match_id']).all():
            raise ValueError(
                "Tried calling evaluation with filter such that filtered data includes rows not in history_df"
            )
        return self.evaluator.evaluate(for_eval_df)

    def run(self, df):
        self.fit(df)
        self.post_process()
        self.validation_evaluation = self._run_evaluation(self.validation_filter)
        self.test_evaluation = self._run_evaluation(self.test_filter)

    def update(self, jd):
        # For now, update just calls fit
        self.fit(jd)
