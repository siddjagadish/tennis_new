from tennis_new.model.config.base import BaseModelConfig


class ELOBaseConfig(BaseModelConfig):

    @property
    def predictor(self):
        # TODO: Implement this!
        raise NotImplementedError()

    @property
    def weighter(self):
        # TODO: Implement this!
        raise NotImplementedError()
