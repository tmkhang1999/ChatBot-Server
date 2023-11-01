from utils.config import ConfigManager
import os

config_path = os.path.join(os.getcwd(), "config.yml")
config_manager = ConfigManager(config_path)
