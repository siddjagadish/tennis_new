from tennis_new.model.config.elo.base import ELOBaseModel


class SetELO(ELOBaseModel):

    @property
    def y(self):
        return ['p1_sets_won', 'p2_sets_won']
