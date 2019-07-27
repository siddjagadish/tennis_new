from tennis_new.model.base import SurfaceWeighter, Surface
from tennis_new.model.config.elo.base import ELOBaseModel


class GrassCourtELO(ELOBaseModel):

    @property
    def weighter(self):
        return SurfaceWeighter({
            Surface.hard.value: 0.5761,
            Surface.clay.value: 0.4121,
            Surface.grass.value: 1.,
            Surface.carpet.value: 0.6713
        })
