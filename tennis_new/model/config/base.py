class BaseModel(object):
    # TODO: Leave room for post-processing / calibrating predictions
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

    @property
    def training_filter(self):
        raise NotImplementedError()

    @property
    def validation_filter(self):
        raise NotImplementedError()

    @property
    def evaluator(self):
        raise NotImplementedError()

    @property
    def test_filter(self):
        raise NotImplementedError()

    @property
    def y(self):
        return None

    def data_validation(self, df):
        # Validate the input data
        pass

    def fit(self, df):
        # Resets and fits predictor based on X, y
        raise NotImplementedError()

    def update(self, df):
        # Updates predictor based on X, y -- not necessarily only new data
        self.predictor.update(df)

    def state_to_dict(self):
        return {
            'predictor_state': self.predictor.state_to_dict()
        }
