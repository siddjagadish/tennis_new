from tennis_new.model.base import SurfaceWeighter, Surface
from tennis_new.model.config.elo.base import ELOBaseModel


class ClayCourtELO(ELOBaseModel):

    @property
    def weighter(self):
        return SurfaceWeighter({
            Surface.hard.value: 0.4838,
            Surface.clay.value: 1.,
            Surface.grass.value: 0.5778,
            Surface.carpet.value: 0.4575
        })
