class BaseModelConfig(object):

    @property
    def predictor(self):
        raise NotImplementedError()

    @property
    def weighter(self):
        raise NotImplementedError()