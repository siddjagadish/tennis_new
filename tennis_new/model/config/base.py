class BaseModel(object):

    def __init__(self, predictor_state=None):
        if predictor_state is not None:
            self.predictor = self.predictor_class(**predictor_state)
        else:
            self.predictor = self.predictor_class(**self.predictor_conf)

    @property
    def predictor_class(self):
        raise NotImplementedError()

    @property
    def predictor_conf(self):
        raise NotImplementedError()

    @property
    def weighter(self):
        raise NotImplementedError()

    def fit(self, X, y=None):
        # Resets and fits predictor based on X, y
        self.predictor = self.predictor_class(**self.predictor_conf)
        self.predictor.fit(X, y)

    def update(self, X, y):
        # Updates predictor based on X, y -- not necessarily only new data
        self.predictor.update(X, y)

    def state_to_dict(self):
        return {
            'predictor_state': self.predictor.state_to_dict()
        }