import logging
import uuid

import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

log = logging.getLogger(__name__)


class Database:
    def __init__(self, host, database, user, password) -> None:
        """
        Initialize the Database object with connection details.

        Args:
            host (str): The database host.
            database (str): The database name.
            user (str): The database user.
            password (str): The database password.
        """
        # Check if all required database variables are provided
        if not all([host, database, user, password]):
            log.error("One or more database variables are missing, exiting...")
            raise SystemExit

        self.url = f"mysql://{user}:{password}@{host}/{database}"

        self.db = self.get()
        self.conversations_table = self.db["conversations"]
        self.users_table = self.db["users"]

        # Initialize tables
        self._setup_tables()

    def get(self) -> dataset.Database:
        """
        Returns the dataset database object.

        Returns:
            dataset.Database: The dataset database object.
        """
        return dataset.connect(url=self.url)

    def _setup_tables(self) -> None:
        """
        Sets up the necessary tables in the database.
        - Creates the database if it doesn't exist.
        - Creates 'users' and 'conversations' tables if missing.
        """
        engine = create_engine(self.url)

        # Create the database if it doesn't already exist
        if not database_exists(engine.url):
            create_database(engine.url)

        # Create 'users' table if missing
        if "users" not in self.db:
            users = self.db.create_table("users")
            users.create_column("user_id", self.db.types.text)
            users.create_column("conversation_ids", self.db.types.json)
            log.info("Created missing table: users")

        # Create 'conversations' table if missing
        if "conversations" not in self.db:
            conversations = self.db.create_table("conversations")
            conversations.create_column("conversation_id", self.db.types.text)
            conversations.create_column("name", self.db.types.text)
            conversations.create_column("history", self.db.types.json)
            log.info("Created missing table: conversations")

        # Commit the changes to the database and close the connection
        self.db.commit()
        self.db.close()

    def add_user(self, user_id, conversation_ids):
        """
        Add a new user to the 'users' table.

        Args:
            user_id (str): The user ID.
            conversation_ids (list): List of conversation IDs associated with the user.
        """
        # Check if the user already exists
        if self.users_table.find_one(user_id=user_id):
            log.warning(f"User with ID {user_id} already exists. Skipping insertion.")
            return

        # Insert new user
        self.users_table.insert(dict(user_id=user_id, conversation_ids=conversation_ids))
        log.info(f"Added user with ID {user_id} to the 'users' table.")

        self.db.commit()
        self.db.close()

    def add_conversation(self, user_id, conversation_id, name):
        """
        Add a new conversation with the provided user ID, conversation ID, and name.

        Args:
            user_id (str): The user ID associated with the conversation.
            conversation_id (str): The unique conversation ID.
            name (str): The name of the conversation.
        """
        # Check if the user exists
        user_record = self.users_table.find_one(user_id=user_id)
        if not user_record:
            log.warning(f"User with ID {user_id} not found. Cannot add conversation.")
            self.db.close()
            return

        # Check if the conversation ID already exists
        if self.conversations_table.find_one(conversation_id=conversation_id):
            log.warning(f"Conversation with ID {conversation_id} already exists. Skipping insertion.")
            self.db.close()
            return

        # Insert the new conversation
        self.conversations_table.insert(
            dict(conversation_id=conversation_id, name=name, history={})
        )

        # Update the user's conversation IDs
        user_conversation_ids = user_record["conversation_ids"]
        user_conversation_ids.append(conversation_id)
        self.users_table.update(
            dict(user_id=user_id, conversation_ids=user_conversation_ids),
            ['user_id']
        )

        log.info(
            f"Added conversation with ID {conversation_id} to the 'conversations' table and linked it to user {user_id}.")

        self.db.commit()
        self.db.close()

    def get_user_conversations(self, user_id):
        """
        Get user's conversations as a dictionary {conversation_id: name}.

        Args:
            user_id (str): The user ID.

        Returns:
            dict: Dictionary of user's conversations {conversation_id: name}.
        """
        user_record = self.users_table.find_one(user_id=user_id)

        if user_record:
            user_conversation_ids = user_record["conversation_ids"]
            user_conversations = {}

            for conversation_id in user_conversation_ids:
                conversation_record = self.conversations_table.find_one(conversation_id=conversation_id)
                if conversation_record:
                    user_conversations[conversation_id] = conversation_record["name"]

            self.db.close()
            return user_conversations

        log.warning(f"User with ID {user_id} not found.")
        self.db.close()
        return None

    def get_history(self, conversation_id):
        """
        Get the saved history for a conversation.

        Args:
            conversation_id (str): The conversation ID.

        Returns:
            dict or None: The saved history for the conversation or None if not found.
        """
        conversation_record = self.conversations_table.find_one(conversation_id=conversation_id)

        if conversation_record:
            history = conversation_record["history"]
            self.db.close()
            return history

        log.warning(f"Conversation with ID {conversation_id} not found.")
        self.db.close()
        return None

    def update_history(self, conversation_id, new_history):
        """
        Update the history for a conversation.

        Args:
            conversation_id (str): The conversation ID.
            new_history (dict): The new history to be updated for the conversation.
        """
        # Check if the conversation exists
        existing_record = self.conversations_table.find_one(conversation_id=conversation_id)

        if existing_record:
            # Update the history for the conversation
            self.conversations_table.update(
                dict(conversation_id=conversation_id, history=new_history),
                ['conversation_id']
            )
            log.info(f"Updated history for conversation with ID {conversation_id}.")

        self.db.commit()
        self.db.close()

    def generate_unique_conversation_id(self, temporary_ids):
        """
        Generate a unique conversation ID not in the 'conversations' table or temporary IDs.

        Args:
            temporary_ids (list): List of temporary conversation IDs to check against.

        Returns:
            str: A unique conversation ID.
        """
        db = self.get()
        conversations_table = db["conversations"]

        while True:
            new_id = str(uuid.uuid4())

            # Check if the ID already exists in the 'conversations' table or temporary IDs
            if not conversations_table.find_one(conversation_id=new_id) and new_id not in temporary_ids:
                db.close()
                return new_id
