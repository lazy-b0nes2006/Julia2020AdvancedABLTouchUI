import RPi.GPIO as GPIO
from decorators import run_async
import time


class BuzzerFeedback(object):
    def __init__(self, buzzerPin):
        GPIO.cleanup()
        self.buzzerPin = buzzerPin
        GPIO.setup(self.buzzerPin, GPIO.OUT)
        GPIO.output(self.buzzerPin, GPIO.LOW)

    @run_async
    def buzz(self):
        GPIO.output(self.buzzerPin, (GPIO.HIGH))
        time.sleep(0.005)
        GPIO.output(self.buzzerPin, GPIO.LOW)

buzzer = BuzzerFeedback(12)



'''
To get the buzzer to beep on button press
'''