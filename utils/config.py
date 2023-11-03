import logging
from os import path
from pyaml_env import parse_config
from dotenv import load_dotenv

log = logging.getLogger(__name__)
load_dotenv()


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.load_config()

    def load_config(self):
        if not path.isfile(self.config_path):
            log.error("Unable to load config.yml, exiting...")
            raise SystemExit

        self.config = parse_config(self.config_path)

    def get(self, key, default=None):
        return self.config.get(key, default)
