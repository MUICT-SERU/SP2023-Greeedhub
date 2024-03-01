import time

from sciroccoclient.httpclient import HTTPClient



class RaspiOLdProgram:

    def __init__(self):

        self.running = True
        self.sleep = 1


    def run(self):
        dds = HTTPClient('https://dds.sandboxwebs.com', 'af12340', 'dd52bb39d5a1bd8f6235dbef7df26d3e')

        while self.running:

            msg = dds.message_queue_pull()

            if msg is not None:
                if msg.message_data['action'] == 'blink':
                    pass
                    time.sleep(5)
                else:
                    pass

            time.sleep(self.sleep)
    

if __name__ == '__main__':

    p = RaspiOLdProgram()
    p.run()