import configparser
import os
import re


class ConfigHandler:
    CONFIG_NAME = "config.ini"
    CONFIG_CATEGORY = "SETTINGS"

    def __init__(self):
        self.setted_up = None
        self.endpoint = None
        self.fetch_interval = None
        self.token = None
        self.hardware_id = None

        self.parser = configparser.ConfigParser()

        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.config = {"Endpoint": "", "Token": "", "HardwareId": "", "SetUp": False}

        self.valid_url_regex = self.url_regex()

    def url_regex(self):
        return re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            # domain...
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

    def is_host_valid(self, url: str) -> bool:
        return re.match(self.valid_url_regex, url) is not None

    def config_exists(self) -> bool:
        """Checks if the config file exists or not"""
        return os.path.exists(self.dir_path + "/" + self.CONFIG_NAME)

    def create_config(self) -> None:
        """Creates a new config file"""

        # Remove old config file to avoid conflicts
        if self.config_exists():
            os.remove(self.dir_path + "/" + self.CONFIG_NAME)

        self.write_config(self.config)

    def load_config(self) -> dict:
        """Loads the configuration file."""
        if not self.config_exists():
            raise FileNotFoundError

        self.parser.read(self.dir_path + "/" + self.CONFIG_NAME)

        self.config["Endpoint"] = self.parser[self.CONFIG_CATEGORY]["Endpoint"]

        if not self.is_host_valid(self.config["Endpoint"]):
            raise Exception("Invalid host")

        self.config["SetUp"] = self.parser.getboolean(self.CONFIG_CATEGORY, "SetUp")
        self.config["Token"] = self.parser[self.CONFIG_CATEGORY]["Token"]
        self.config["HardwareId"] = self.parser[self.CONFIG_CATEGORY]["HardwareId"]

        # cleanup
        self.config["Endpoint"] = self.config["Endpoint"].replace('"', "")

        return self.config

    def write_config(self, config) -> None:
        """Write the configuration file"""
        self.config = config

        self.parser[self.CONFIG_CATEGORY] = config
        with open(self.dir_path + "/" + self.CONFIG_NAME, "w") as configfile:
            self.parser.write(configfile)
