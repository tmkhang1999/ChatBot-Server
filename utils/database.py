import logging

import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

log = logging.getLogger(__name__)


class Database:
    def __init__(self, host, database, user, password) -> None:
        self.host = host
        self.database = database
        self.user = user
        self.password = password

        if not all([self.host, self.database, self.user, self.password]):
            log.error("One or more database variables are missing, exiting...")
            raise SystemExit

        self.url = f"mysql://{self.user}:{self.password}@{self.host}/{self.database}"

    def get(self) -> dataset.Database:
        """Returns the dataset database object."""
        return dataset.connect(url=self.url)

    def setup(self) -> None:
        """Sets up the tables needed."""
        # Create the database if it doesn't already exist.
        engine = create_engine(self.url)
        if not database_exists(engine.url):
            create_database(engine.url)

        # Open a connection to the database.
        db = self.get()

        # Create tables and columns to store the user-related variables as a JSON object.
        if "conversations" not in db:
            users = db.create_table("conversations")
            users.create_column("conversation_id", db.types.text)
            users.create_column("memory", db.types.json)
            log.info("Created missing table: conversations")

        # Commit the changes to the database and close the connection.
        db.commit()
        db.close()
