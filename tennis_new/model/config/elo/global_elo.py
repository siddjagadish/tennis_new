from tennis_new.model.base import DummyWeighter
from tennis_new.model.config.elo.base import ELOBaseModel


class GlobalELO(ELOBaseModel):

    @property
    def weighter(self):
        return DummyWeighter()