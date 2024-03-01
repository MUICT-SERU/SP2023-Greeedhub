#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

from sciroccoclient.clients import HTTPClient



class RaspiOLdProgram:

    def __init__(self):

        self.running = True
        self.sleep = 0.01

    def run(self):
        scirocco_client = HTTPClient('https://dds.sandboxwebs.com', 'af2', 'dd52bb39d5a1bd8f6235dbef7df26d3e')
        led_control = LedControl(11, 0.1)

        while self.running:
            try:
                msg = scirocco_client.pull()

                if msg is not None:
                    action = msg.payload['action']
                    if action == 'blink':
                        led_control.blink()
                    elif action == 'poweron':
                        led_control.on()
                    elif action == 'poweroff':
                        led_control.off()
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
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        
    def blink(self):
        self.on()
        time.sleep(self.blink_interval)
        self.off()
        time.sleep(self.blink_interval)
        return

    def clean(self):
        GPIO.cleanup()


if __name__ == '__main__':

    p = RaspiOLdProgram()
    p.run()
