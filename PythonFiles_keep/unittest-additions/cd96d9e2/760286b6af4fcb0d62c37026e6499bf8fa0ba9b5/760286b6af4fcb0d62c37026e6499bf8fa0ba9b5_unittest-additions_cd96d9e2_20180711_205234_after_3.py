
class AdditionalAssertsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assertIsEmpty(self, collection, msg=None):
        if len(collection) > 0:
            msg = self._formatMessage(msg, f'{type(collection).__name__} is not empty.')
            raise self.failureException(msg)

    def assertIsNotEmpty(self, collection, msg=None):
        if len(collection) < 1:
            msg = self._formatMessage(msg, f'{type(collection).__name__} is empty.')
            raise self.failureException(msg)
    