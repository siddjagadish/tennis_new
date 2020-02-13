class Filter(object):

    sub_filters = []

    @classmethod
    def keep_condition(cls, df):
        # Combines conditions of subfilters
        # Overwritten for single filter
        out = True
        for sf in cls.sub_filters:
            out &= sf.keep_condition(df)
        return out

    @classmethod
    def filter(cls, df):
        return df[cls.keep_condition(df)]


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
        MissingPIDFilter,
        MissingScoreFilter
    ]
