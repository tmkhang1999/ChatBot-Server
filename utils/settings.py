from utils.config import ConfigManager
from utils.database import Database
import os

# Set up config
config_path = os.path.join(os.path.dirname(__file__), "config.yml")
config_manager = ConfigManager(config_path)

# Set up database
db_info = config_manager.get("database")
database = Database(db_info["host"], db_info["database"], db_info["user"], db_info["password"])
