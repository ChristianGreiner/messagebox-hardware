import json
import logging
import os
import random
import string
import sys
import threading
import time
from enum import Enum
from logging.handlers import RotatingFileHandler

import requests

from gpiozero import Button
from ServoMotor import ServoMotor

from const import HARDWARE_ID_LENGTH, SERVO_ROTATION_SPEED
from ConfigHandler import ConfigHandler
from DisplayRenderer import DisplayRenderer
from NetworkManager import (InvalidResponseError, InvalidTokenError,
                            NetworkManager, UnauthenticatedError)


class State(Enum):
    LOAD_CONFIG = 1
    FETCH_MESSAGES = 2
    REGISTER_DEVICE = 3
    NOTIFY = 4
    READING = 5


class Messagebox(object):

    def __init__(self, display, trigger_pin: int, servo_pin: int):

        self.setup_logging()
        self.config = {}
        self.last_message = {}

        self.muted = False
        self.rotation_count = 1
        self.fetch_interval = 60
        self.rotation_interval = 30
        
        self.servo_thread = None

        self.network = NetworkManager(None)
        self.config_handler = ConfigHandler()

        self.display = display
        self.display_renderer = DisplayRenderer(display)
        self.button = Button(trigger_pin)
        self.servo = ServoMotor(servo_pin)

        self.current_state = State.LOAD_CONFIG
        
        self.display_renderer.draw_multi_line_center_text("MESSAGEBOX", 18)
        time.sleep(3)

    def setup_logging(self) -> None:

        if not os.path.exists("logs"):
            os.mkdir("logs")

        rfh = logging.handlers.RotatingFileHandler(
            filename="logs/messagebox.log",
            mode="a",
            maxBytes=25000000,  # 25 Megabyte
            backupCount=2,
            encoding=None,
            delay=0,
        )
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(message)s",
            level=logging.DEBUG,
            datefmt="%y-%m-%d %H:%M:%S",
            handlers=[rfh],
        )
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    def run(self) -> None:
        logging.info("Messagebox started")

        while True:
            if self.current_state is State.LOAD_CONFIG:
                self.current_state = self.load_config()

            elif self.current_state is State.REGISTER_DEVICE:
                self.current_state = self.register_state()

            elif self.current_state is State.NOTIFY:
                self.current_state = self.notify_state()

            elif self.current_state is State.READING:
                self.current_state = self.reading_state()

            elif self.current_state is State.FETCH_MESSAGES:
                self.current_state = self.fetch_messages_state()

            logging.info("Current State: " + str(self.current_state))

    def generate_hardware_id(self) -> str:
        return "".join(random.choice(string.digits) for i in range(HARDWARE_ID_LENGTH))

    def load_config(self):
        """Loads the config"""
        logging.info("Loading config file")

        # Exit because no endpoint is set.
        if not self.config_handler.config_exists():
            self.config_handler.create_config()

        self.config = self.config_handler.load_config()

        if not self.config["Endpoint"]:
            logging.critical("API-Server not found")
            exit(0)

        if not self.config["HardwareId"]:
            self.config["HardwareId"] = self.generate_hardware_id()
            logging.info("Generating Hardware ID:" + self.config["HardwareId"])

        self.network.endpoint = self.config["Endpoint"]
        self.network.token = self.config["Token"]

        logging.info("Endpoint: " + str(self.network.endpoint))
        logging.info("Token: " + str(self.network.token))

        if self.config["SetUp"]:
            return State.FETCH_MESSAGES
    
        return State.REGISTER_DEVICE

    def register_state(self):
        """Registers the box in the backend to receive messages"""
        logging.info("Register box...")

        hardware_id = self.config["HardwareId"]
        print("Hardware ID:" + hardware_id)

        # add space after every 3rd number 
        id_text = str(" ".join(a + b + c for a, b, c in zip(hardware_id[::3], hardware_id[1::3], hardware_id[2::3])))
        self.display_renderer.draw_center_text(f"Personal ID:\n{id_text}", 18)

        token = self.network.register_device(hardware_id)

        if token:
            logging.info("Received token: " + token)
            self.network.token = token
            self.config["SetUp"] = True
            self.config["Token"] = token
            self.config_handler.write_config(self.config)

            self.display_renderer.draw_multi_line_center_text("DEVICE REGISTERED", 18)
            
            time.sleep(3)

            return State.FETCH_MESSAGES

        time.sleep(10)

        return State.REGISTER_DEVICE

    def fetch_messages_state(self):
        """Fetchs for new messages"""
        logging.info("Fetching messages...")

        try:
            if self.last_message and not self.muted:
                if "message" in self.last_message:
                    if len(self.last_message["message"]) > 0:
                        return State.NOTIFY

            self.last_message = self._fetch_messages()

            if self.last_message:
                if self.muted:
                    self.display_renderer.draw_multi_line_center_text("DEVICE MUTED", 18)
                else:
                    self.display_renderer.draw_multi_line_center_text("NO MESSAGES", 18)

                if "message" in self.last_message:
                    logging.info("Last message: " + json.dumps(self.last_message))

                    msg_obj = self.last_message["message"]
                    if len(msg_obj) > 0:
                        message_text = msg_obj["text"]
                        author = msg_obj["author"]["name"]
                        text_color = msg_obj["text_color"]
                        bg_color = msg_obj["background_color"]
                        
                        self.display_renderer.draw_message_text(
                            message_text, author, text_color, bg_color
                        )

                        if self.muted:
                            return State.FETCH_MESSAGES

                        return State.NOTIFY

            time.sleep(self.fetch_interval)

            return State.FETCH_MESSAGES
        except requests.ConnectionError as ex:
            logging.error("No Connection... try again")
            logging.error(ex)

            self.display_renderer.draw_center_text("No connection")
            time.sleep(5)

            self.current_state = State.FETCH_MESSAGES
            self.run()

        except UnauthenticatedError:
            logging.error("Unauthenticated")

            self.current_state = State.REGISTER_DEVICE
            self.run()

        except InvalidResponseError as ex:
            logging.error("Invalid Response: " + ex)

            self.current_state = State.FETCH_MESSAGES
            self.run()
        
        except InvalidTokenError:
            logging.error("Invalid Token")

            self.current_state = State.REGISTER_DEVICE
            self.run()


    def notify_state(self):
        """Notifies the user by rotating the servo motor"""
        logging.info("Notify user...")

        self.servo_thread = threading.Thread(target=self._rotate_servo, args=())
        self.servo_thread.start()
        self.servo_thread.do_run = True

        while True:
            if not self.button.is_pressed:
                self.servo_thread.do_run = False
                logging.info("Box opend")

                return State.READING
            time.sleep(0.1)

    def reading_state(self):
        """Waits till the user opens the box and sends a request"""
        logging.info("Sending reading request")

        if self.last_message:
            if "message" in self.last_message:
                if len(self.last_message["message"]) > 0:
                    message_id = self.last_message["message"]["id"]
                    self.network.read_message(message_id)
                    self.last_message = {}

                    # wait till box is closed
                    logging.info("Waiting for box is closed")
                    while True:
                        if self.button.is_pressed:
                            logging.info("Box closed!")

                            return State.FETCH_MESSAGES
                        time.sleep(0.1)

        return State.FETCH_MESSAGES

    def _rotate_servo(self):
        if self.servo:
            self.servo.rotate(0)

            logging.info("Rotating servo")
            while getattr(self.servo_thread, "do_run", True):
                muted = False
                response = self._fetch_messages()
                if response:
                    if "mute" in response["settings"]:
                        muted = bool(response["settings"]["mute"])

                if not muted:
                    for i in range(self.rotation_count):
                        time.sleep(SERVO_ROTATION_SPEED)
                        self.servo.rotate(180)
                        time.sleep(SERVO_ROTATION_SPEED)
                        self.servo.rotate(0)
                        time.sleep(SERVO_ROTATION_SPEED)
                
                time.sleep(5)

    def _fetch_messages(self):
        response = self.network.fetch_messages()
        if response:
            if "settings" in response:
                settings = response["settings"]
                if "mute" in settings:
                    self.muted = bool(settings["mute"])
                if "rotation_count" in settings:
                    self.rotation_count = int(settings["rotation_count"])
                if "fetch_interval" in settings:
                    self.fetch_interval = int(settings["fetch_interval"])
                if "rotation_interval" in settings:
                    self.rotation_interval = int(settings["rotation_interval"])
        return response

