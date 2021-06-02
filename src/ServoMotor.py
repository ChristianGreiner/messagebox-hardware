import threading
import time

import RPi.GPIO as GPIO


class ServoMotor:
    def __init__(self, data_pin: int):
        self.data_pin = data_pin

        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT)

        self.pulse = 50  # 50Hz

        self.servo = GPIO.PWM(self.data_pin, self.pulse)
        self.servo.start(0)

    def rotate(self, angle: float):
        if 0 <= angle <= 180:
            self.servo.ChangeDutyCycle(2 + (angle / 18))
            time.sleep(0.25)
            self.servo.ChangeDutyCycle(0)

    def reset(self):
        self.servo.stop()
        GPIO.cleanup()
