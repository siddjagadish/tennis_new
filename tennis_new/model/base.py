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