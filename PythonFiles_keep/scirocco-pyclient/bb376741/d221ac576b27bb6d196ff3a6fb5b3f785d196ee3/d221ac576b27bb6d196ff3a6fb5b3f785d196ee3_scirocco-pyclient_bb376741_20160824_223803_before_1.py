import RPi.GPIO as GPIO
import time
from sciroccoclient.httpclient import HTTPClient


class RaspiOLdProgram:
    def __init__(self):
        self.running = True
        self.sleep = 1

    def run(self):

        dds = HTTPClient('https://dds.sandboxwebs.com', 'af12343', 'dd52bb39d5a1bd8f6235dbef7df26d3e')

        while self.running:

            msg = dds.message_queue_pull()

            if msg is not None:
                if msg.message_data['action'] == 'blink':
                    pass
                    time.sleep(5)
                else:
                    pass

            time.sleep(self.sleep)


class UltrasonicSensor:
    PIN_TRIG = 23
    PIN_ECHO = 24

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_TRIG, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        time.sleep(2)

    def make_measurement(self):

        self.send_pulse()
        res = self.check_pulse_return_time()
        result_in_cm = self.make_measurement(res[0], res[1])
        return result_in_cm

    def send_pulse(self):

        GPIO.output(self.PIN_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.PIN_TRIG, False)

    def check_pulse_return_time(self):

        while GPIO.output(self.PIN_ECHO) == 0:
            pulse_start = time.time()
        while GPIO.output(self.PIN_ECHO) == 1:
            pulse_end = time.time()

        return (pulse_start, pulse_end)

    def do_math_cm(self, pstart, pend):

        duration = pend - pstart
        distance_meters = (duration * 340) / 2
        distance_cm = distance_meters * 100

        return distance_cm


if __name__ == '__main__':
    p = RaspiOLdProgram()
    p.run()
