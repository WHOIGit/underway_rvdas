from logger.transforms.transform import Transform

class CustomFunctionTransform(Transform):
    """
    Apply a custom function to a record
    """
    def __init__(self, func):
        self.func = func

    def transform(self, record):
        self.func(record)