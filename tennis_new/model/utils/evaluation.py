import pandas as pd
from tennis_new.model.utils.filters import PossibleWalkoverFilter
from tennis_new.model.utils.metrics import (
    AUCMetric,
    AccuracyMetric
)


def get_test_set(df, test_min='2011-01-01', test_max='2015-01-01', test_surface=None, filter_walkovers=True):
    date_cond = (
            (df['date'] >= test_min) &
            (df['date'] < test_max)
    )
    surface_cond = True
    if test_surface is not None:
        surface_cond = df['surface'] == test_surface
    cond = date_cond & surface_cond
    if filter_walkovers:
        cond &= (PossibleWalkoverFilter.keep_condition(df))
    return df[cond]


def eval_mod(mod, df, test_min='2011-01-01', test_max='2015-01-01', test_surface=None, filter_walkovers=False):
    # TODO: Filter out walkovers from test set
    # TODO: Create Evaluator class for betting performance
    history_df = pd.DataFrame(mod.history)
    test_set = get_test_set(
        df,
        test_min=test_min,
        test_max=test_max,
        test_surface=test_surface,
        filter_walkovers=filter_walkovers
    )
    test_set = pd.merge(test_set, history_df, left_on='match_link', right_on='match_id')

    accuracy = (test_set['elo_match_prediction'] > 0.5).mean()
    w_odds = test_set[
        test_set['p1_odds'].notnull() &
        test_set['p2_odds'].notnull() &
        (test_set['p1_odds'] != test_set['p2_odds'])
        ]
    n_w_odds = w_odds.shape[0]
    odds_accuracy = (w_odds['p1_odds'] <= w_odds['p2_odds']).mean()
    mod_odds_accuracy = (w_odds['elo_match_prediction'] > 0.5).mean()
    return {
        'overall_accuracy': accuracy,
        'odds_accuracy': odds_accuracy,
        'model_odds_accuracy': mod_odds_accuracy,
        'n_w_odds': n_w_odds
    }


class Evaluator(object):

    def __init__(self, *prediction_cols):
        # List of prediction columns to compare
        self.prediction_cols = prediction_cols

    @property
    def metrics(self):
        # List of metrics to use for evaluation
        raise NotImplementedError()

    def evaluate(self, df):
        out = {}
        for pred_col in self.prediction_cols:
            for metric in self.metrics:
                out.update(metric.calculate_metric(df, pred_col))
        return out


class BasicEvaluator(Evaluator):

    @property
    def metrics(self):
        return [
            AUCMetric(),
            AccuracyMetric()
        ]
