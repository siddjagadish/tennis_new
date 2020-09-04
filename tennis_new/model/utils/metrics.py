from tennis_new.model.utils.filters import DummyFilter
from sklearn.metrics import roc_auc_score


class Metric(object):

    @property
    def data_filter(self):
        DummyFilter

    def _metric(self, df):
        raise NotImplementedError()

    def calculate_metric(df):
        filtered_df = self.data_filter.filter_data(df)
        return {
            self.__name__: self._metric(filtered_df)
        }


class AUCMetric(object):
    '''
    For pairwise comparison models, we run into an issue
    of some metrics (AUC) depending on how we've labeled points.
    For the AUC, we simply duplicate our data, creating data where
    each point is a 0 and where each point is a 1.
    '''
    def _metric(self, df, pred_col):
        preds = filtered_df[pred_col]
        n = len(preds)
        y = np.concatenate([
            np.ones(n), np.zeros(n)
        ])
        y_hat = np.concatenate([
            preds,
            1. - preds
        ])
        return roc_auc_score(y, y_hat)


class AccuracyMetric(object):

    def _metric(self, df, pred_col):
        # NOTE: Could use >= in line below?
        return (filtered_df[pred_col] > 0.5).mean()
