import anachronos


class AnachronosServer(object):

    def listen(self):
        raise NotImplementedError




class NamedPipeAnachronosServer(AnachronosServer):

    def __init__(self, pipe_file: str, message_queue=None):
        self.pipe_file = pipe_file
        self.message_queue = message_queue or anachronos.anachronos

    def listen(self):
        with open(self.pipe_file, 'r') as pipe:
            for line in iter(pipe.readline, b''):
                self.message_queue.store(line)
