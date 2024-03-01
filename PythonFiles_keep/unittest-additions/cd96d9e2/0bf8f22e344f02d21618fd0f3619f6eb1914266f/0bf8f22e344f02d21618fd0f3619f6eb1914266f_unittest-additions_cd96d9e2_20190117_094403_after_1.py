import os

def fix_iteration_in_mock_open(open_mock):
  """ A test utility function to help with file open mocking.
  """
  open_mock.return_value.__iter__ = lambda self : iter(self.readline, '')


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


class TemporaryFile:
    def __init__(self, filepath, content):
        if os.path.exists(filepath):
            raise AssertionError('Temporary file target already exists: ' + filepath)
        self.filepath = filepath
        self._initial_content = content

    def __enter__(self):
        self.append(self._initial_content)
        return self

    def __exit__(self, *args):
        os.remove(self.filepath)

        if os.path.exists(self.filepath):
            raise AssertionError('Failed to delete temporary file: ' + self.filepath)

    def append(self, content):
        with open(self.filepath, 'a') as f:
            f.write(content)
