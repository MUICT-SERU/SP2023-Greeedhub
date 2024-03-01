#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
from sciroccoclient.httpclient import HTTPClient


class RaspiOLdProgram:
    def __init__(self):
        self.running = True
        self.sleep = 1

    def run(self):
        us = UltrasonicSensor(23, 24)
        dds = HTTPClient('https://dds.sandboxwebs.com', 'af12343', 'dd52bb39d5a1bd8f6235dbef7df26d3e')

        while self.running:

            try:
                msg_template = {"to_node_id": "", "data": {"measurement": us.make_measurement()}}
                msg_template['to_node_id'] = 'af12344'
                dds.message_queue_push(msg_template)
                msg_template['to_node_id'] = 'af12345'
                dds.message_queue_push(msg_template)
                time.sleep(self.sleep)
            except KeyboardInterrupt:
                self.running = False
                print("Shutting down measurement system")


class UltrasonicSensor:
    def __init__(self, pin_trigger, pin_echo):

        self.PIN_TRIG = pin_trigger
        self.PIN_ECHO = pin_echo

    def setup_sensor(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_TRIG, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        GPIO.output(self.PIN_TRIG, False)

        time.sleep(2)

    def clean(self):

        GPIO.cleanup()

    def make_measurement(self):

        try:

            self.setup_sensor()
            self.send_pulse()
            res = self.check_pulse_return_time()
            self.clean()
            result_in_cm = self.do_math_cm(res[0], res[1])

            return result_in_cm
        except KeyboardInterrupt:
            self.clean()
            raise KeyboardInterrupt

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
        distance_meters = (duration * 343) / 2
        distance_cm = round((distance_meters * 100), 2)

        return distance_cm


if __name__ == '__main__':
    p = RaspiOLdProgram()
    p.run()
