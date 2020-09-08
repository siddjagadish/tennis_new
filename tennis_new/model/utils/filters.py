import numpy as np


class Filter(object):

    sub_filters = []

    def keep_condition(self, df):
        # Combines conditions of subfilters
        # Overwritten for single filter
        out = True
        for sf in self.sub_filters:
            if isinstance(sf, type):
                raise TypeError("sub_filters must be list of Filter instances, not types")
            out &= sf.keep_condition(df)
        return out

    def filter_data(self, df):
        return df[self.keep_condition(df)]


class MissingScoreFilter(Filter):

    @classmethod
    def keep_condition(cls, df):
        return (
                df['p1_sets_won'].notnull() &
                df['p2_sets_won'].notnull()
        )


class PossibleWalkoverFilter(Filter):

    @classmethod
    def keep_condition(cls, df):
        possible_walkover = (
                (df['p1_sets_won'] == 1) &
                df['p1_set1'].isnull()
        )
        return ~possible_walkover


class RetirementFilter(Filter):

    @classmethod
    def keep_condition(cls, df):
        retirement = (
                (df['p1_sets_won'] == 1) &
                df['p1_set1'].notnull()
        )
        return ~retirement


class MissingPIDFilter(Filter):

    @classmethod
    def keep_condition(cls, df):
        return (
                df['p1_link'].notnull() &
                df['p2_link'].notnull()
        )


class TrainingFilter(Filter):

    sub_filters = [
        MissingPIDFilter(),
        MissingScoreFilter()
    ]


class DummyFilter(Filter):
    # Filter that keeps everything

    @classmethod
    def keep_condition(cls, df):
        return np.ones(len(df), dtype=bool)


class DateFilter(Filter):

    def __init__(self, min_date=None, max_date=None):
        if min_date is None and max_date is None:
            raise ValueError("At least one of min_date and max_date must be specified")
        if min_date is None:
            self.min_date = '1700-01-01'  # Very old date
        if max_date is None:
            self.max_date = '9999-01-01'  # Very new date
        self.min_date = min_date
        self.max_date = max_date

    def keep_condition(self, df):
        return (
            (df['date'] >= self.min_date) &
            (df['date'] < self.max_date)
        )


class SurfaceFilter(Filter):

    def __init__(self, surface, include_na=False):
        self.surface = surface
        self.include_na = include_na

    def keep_condition(self, df):
        cond = df['surface'] == self.surface
        if self.include_na:
            cond = cond | df['surface'].isnull()


class HasOddsFilter(Filter):

    @classmethod
    def keep_condition(cls, df):
        return (
            df['p1_odds'].notnull() &
            df['p2_odds'].notnull()
        )
