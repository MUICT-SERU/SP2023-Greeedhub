#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
from sciroccoclient.httpclient import HTTPClient


class RaspiOLdProgram:
    def __init__(self):
        self.running = True
        self.sleep = 0.18
        self.threshold = 2
    def message_led_action(self, destination, action):
       	
        msg = {"to_node_id": destination, "data": {"action": action}}
        return msg
    
    def check_distance_change(self, last_measurement, measurement):
        if (last_measurement + self.threshold) < measurement:
            return True
        elif (last_measurement - self.threshold) > measurement:
            return True
        else:
            return False		

    def run(self):
        us = UltrasonicSensor(23, 24)
        scirocco_client = HTTPClient('https://dds.sandboxwebs.com', 'af1', 'dd52bb39d5a1bd8f6235dbef7df26d3e')
        last_measurement = us.make_measurement()
        while self.running:

            try:

                measurement = us.make_measurement()
                if self.check_distance_change(last_measurement, measurement):

                    print(measurement)

                    if measurement <= 20:
                        scirocco_client.push(self.message_led_action('af2', 'poweron'))
                    else:                    
                        scirocco_client.push(self.message_led_action('af2', 'poweroff'))

                    if measurement <= 30:
                    
                        scirocco_client.push(self.message_led_action('af3', 'poweron'))
                    else:
                        scirocco_client.push(self.message_led_action('af3', 'poweroff'))
                
                last_measurement = measurement
                time.sleep(self.sleep)
            except KeyboardInterrupt:
                self.running = False
                print("Shutting down measurement system")


class UltrasonicSensor:
    def __init__(self, pin_trigger, pin_echo):

        self.PIN_TRIG = pin_trigger
        self.PIN_ECHO = pin_echo
        self.setup_sensor()

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

            self.send_pulse()
            res = self.check_pulse_return_time()
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
