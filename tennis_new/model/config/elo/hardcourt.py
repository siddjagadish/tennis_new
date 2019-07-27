from tennis_new.model.base import SurfaceWeighter, Surface
from tennis_new.model.config.elo.base import ELOBaseConfig


class HardCourtELO(ELOBaseConfig):

    @property
    def weighter(self):
        return SurfaceWeighter({
            Surface.hard.value: 1.,
            Surface.clay.value: 0.3995,
            Surface.grass.value: 0.6927,
            Surface.carpet.value: 0.662
        })