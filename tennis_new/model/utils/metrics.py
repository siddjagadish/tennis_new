import numpy as np
from sklearn.metrics import roc_auc_score
from enum import Enum


class NullHandle(Enum):

    default_handling = 'default_handling',
    set_to_none = 'set_to_none'
    throw_error = 'throw_error'


class Metric(object):

    @property
    def null_handling(self):
        return NullHandle.set_to_none

    def _metric(self, df):
        raise NotImplementedError()

    def calculate_metric(self, df, pred_col):
        metric_name = '%s_%s' % (pred_col, self.__class__.__name__)
        if df[pred_col].isnull().any():
            if self.null_handling == NullHandle.set_to_none:
                return {
                    metric_name: None
                }
            elif self.null_handling == NullHandle.throw_error:
                    raise ValueError("Tried to call %s on null prediction" % metric_name)
        return {
            metric_name: self._metric(df, pred_col)
        }


class AUCMetric(Metric):
    '''
    For pairwise comparison models, we run into an issue
    of some metrics (AUC) depending on how we've labeled points.
    For the AUC, we simply duplicate our data, creating data where
    each point is a 0 and where each point is a 1.
    '''

    def _metric(self, df, pred_col):
        preds = df[pred_col]
        n = len(preds)
        y = np.concatenate([
            np.ones(n), np.zeros(n)
        ])
        y_hat = np.concatenate([
            preds,
            1. - preds
        ])
        return roc_auc_score(y, y_hat)


class AccuracyMetric(Metric):

    def _metric(self, df, pred_col):
        # NOTE: Could use >= in line below?
        return (df[pred_col] > 0.5).mean()
