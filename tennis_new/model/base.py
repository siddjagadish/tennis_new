import numpy as np
import pandas as pd
from enum import Enum


class Weighter(object):

    @property
    def required_columns(self):
        raise NotImplementedError()

    def assert_required_columns(self, df):
        if not all([x in df for x in self.required_columns]):
            missing_cols = [x for x in self.required_columns if x not in df]
            raise ValueError("DataFrame missing required columns %s" % str(missing_cols))

    def weight(self, df):
        raise NotImplementedError()


class SurfaceWeighter(Weighter):

    def __init__(self, weight_dict):
        # TODO: Check Surface Keys Make Sense
        self.weight_dict = weight_dict

    @property
    def required_columns(self):
        return [
            'tourney_surface'
        ]

    def weight(self, df):
        return df['tourney_surface'].map(lambda x: self.weight_dict[x]).values

    def state_to_dict(self):
        return {
            'weight_dict': self.weight_dict
        }


class Surface(Enum):

    clay = 'Clay'
    hard = 'Hard'
    carpet = 'Carpet'
    grass = 'Grass'


def get_val_test_for_surface(df, surface, n=10000, min_length_days=365, atp_only=False):
    # Gets the indices for the validation and test set
    if atp_only:
        allowed_tours = ['atp']
    else:
        allowed_tours = ['atp', 'challenger']

    total_on_surface = (
            (df['tourney_surface'] == surface) &
            df['tour_type'].isin(allowed_tours)
    ).sum()
    n_test_on_surface = total_on_surface - (
            (df['tourney_surface'] == surface) &
            df['tour_type'].isin(allowed_tours)
    ).cumsum()
    indexer = np.arange(df.shape[0])

    n_test_start_idx = np.where(n_test_on_surface > n)[0][-1]
    date_test_start = pd.to_datetime(df['tourney_dates'].max()) - pd.Timedelta(days=min_length_days)
    date_test_start_idx = np.where(pd.to_datetime(df['tourney_dates']) > date_test_start)[0][0]
    test_start_idx = min(n_test_start_idx, date_test_start_idx)
    test_idx = np.where(
        (indexer >= test_start_idx) &
        (df['tourney_surface'] == surface) &
        (df['tour_type'].isin(allowed_tours))
    )[0]

    n_test = n_test_on_surface.iloc[test_start_idx]
    test_start_date = pd.to_datetime(df['tourney_dates'].iloc[test_start_idx])

    n_val_start_idx = np.where(n_test_on_surface > n_test + n)[0][-1]
    date_val_start = pd.to_datetime(test_start_date - pd.Timedelta(days=min_length_days))
    date_val_start_idx = np.where(pd.to_datetime(df['tourney_dates']) > date_val_start)[0][0]
    val_start_idx = min(n_val_start_idx, date_val_start_idx)
    val_idx = np.where(
        (indexer >= val_start_idx) &
        (indexer < test_start_idx) &
        (df['tourney_surface'] == surface) &
        (df['tour_type'].isin(allowed_tours))
    )[0]

    return val_idx, test_idx