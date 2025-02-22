import os
import urllib.parse
from langchain_community.utilities import SQLDatabase
from utils.config import ConfigManager

# Set up config
config_path = os.path.join(os.path.dirname(__file__), "config.yml")
config_manager = ConfigManager(config_path)

# Connect to the host database
planz_db_info = config_manager.get("planz_db")
encoded_password = urllib.parse.quote_plus(planz_db_info["password"])
url = f"mysql+pymysql://{planz_db_info['user']}:{encoded_password}@{planz_db_info['host']}:{planz_db_info['port']}/{planz_db_info['database']}"
planz_db = SQLDatabase.from_uri(url, include_tables=planz_db_info["tables"])
print("Successfully connect to PlanZ database")
