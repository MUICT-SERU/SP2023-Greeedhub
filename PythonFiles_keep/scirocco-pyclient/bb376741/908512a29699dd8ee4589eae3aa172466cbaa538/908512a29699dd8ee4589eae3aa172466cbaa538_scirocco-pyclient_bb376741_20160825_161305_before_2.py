#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

from sciroccoclient.httpclient import HTTPClient



class RaspiOLdProgram:

    def __init__(self):

        self.running = True
        self.sleep = 1

    def run(self):
        dds = HTTPClient('https://dds.sandboxwebs.com', 'af2', 'dd52bb39d5a1bd8f6235dbef7df26d3e')
        led_control = LedControl(11, 0.2)

        while self.running:
            try:
                msg = dds.message_queue_pull()

                if msg is not None:
                    if msg.message_data['action'] == 'blink':
                        led_control.blink()
                time.sleep(self.sleep)

            except KeyboardInterrupt:

                led_control.clean()
                self.running = False
                print("Shutting down system .....")


class LedControl:

    def __init__(self, pin, blink_interval):

        self.pin = pin
        self.blink_interval = blink_interval
        GPIO.setmode(GPIO.BOARD)

    def blink(self):
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(self.blink_interval)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(self.blink_interval)
        return

    def clean(self):
        GPIO.cleanup()


if __name__ == '__main__':

    p = RaspiOLdProgram()
    p.run()