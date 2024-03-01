import RPi.GPIO as GPIO
import time
#from sciroccoclient.httpclient import HTTPClient TODO ERROR IMPORT IN RASPI


class RaspiOLdProgram:
    def __init__(self):
        self.running = True
        self.sleep = 1

    def run(self):
        us = UltrasonicSensor(23, 24)

        # dds = HTTPClient('https://dds.sandboxwebs.com', 'af12343', 'dd52bb39d5a1bd8f6235dbef7df26d3e')

        while self.running:
            print(us.make_measurement())

            """msg = dds.message_queue_pull()

            if msg is not None:
                if msg.message_data['action'] == 'blink':
                    pass
                    time.sleep(5)
                else:
                    pass
            """
            time.sleep(self.sleep)


class UltrasonicSensor:
    def __init__(self, pin_trigger, pin_echo):

        self.PIN_TRIG = pin_trigger
        self.PIN_ECHO = pin_echo

    def setup_sensor(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_TRIG, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        time.sleep(2)

    def clean(self):

        GPIO.cleanup()

    def make_measurement(self):

        self.clean()

        self.setup_sensor()
        self.send_pulse()
        res = self.check_pulse_return_time()
        result_in_cm = self.make_measurement(res[0], res[1])
        self.clean()
        return result_in_cm

    def send_pulse(self):

        GPIO.output(self.PIN_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.PIN_TRIG, False)

    def check_pulse_return_time(self):

        while GPIO.input(self.PIN_ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(self.PIN_ECHO) == 1:
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
