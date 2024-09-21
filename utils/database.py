import json
import logging
import uuid

import dataset
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

log = logging.getLogger(__name__)


class Database:
    def __init__(self, host, database, user, password) -> None:
        """
        Initialize the Database object with connection details.
        """
        # Check if all required database variables are provided
        if not all([host, database, user, password]):
            log.error("One or more database variables are missing, exiting...")
            raise SystemExit

        self.url = f"mysql+pymysql://{user}:{password}@{host}/{database}"

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

        db = self.get()

        # Create 'users' table if missing
        if "users" not in db:
            users = db.create_table("users")
            users.create_column("user_id", db.types.text)
            users.create_column("conversation_ids", db.types.json)
            log.info("Created missing table: users")
            print("Created missing table: users")

        # Create 'conversations' table if missing
        if "conversations" not in db:
            conversations = db.create_table("conversations")
            conversations.create_column("conversation_id", db.types.text)
            conversations.create_column("name", db.types.text)
            conversations.create_column("history", db.types.json)
            log.info("Created missing table: conversations")
            print("Created missing table: conversations")

        # Commit the changes to the database and close the connection
        db.commit()
        db.close()

        print("Successfully set up the tables for AI database")

    def add_user(self, user_id, conversation_ids):
        """
        Add a new user to the 'users' table.

        Args:
            user_id (str): The user ID.
            conversation_ids (list): List of conversation IDs associated with the user.
        """
        db = self.get()
        users_table = db["users"]

        # Check if the user already exists
        if users_table.find_one(user_id=user_id):
            db.close()
            raise HTTPException(status_code=409,
                                detail=f"User with ID {user_id} already exists. Skipping insertion.")

        # Insert new user
        users_table.insert(dict(user_id=user_id, conversation_ids=json.dumps(conversation_ids)))
        log.info(f"Added user with ID {user_id} to the 'users' table.")

        db.commit()
        db.close()

    def add_conversation(self, user_id, conversation_id, name):
        """
        Add a new conversation with the provided user ID, conversation ID, and name.

        Args:
            user_id (str): The user ID associated with the conversation.
            conversation_id (str): The unique conversation ID.
            name (str): The name of the conversation.
        """
        db = self.get()
        users_table = db["users"]
        conversations_table = db["conversations"]

        # Check if the user exists
        user_record = users_table.find_one(user_id=user_id)
        if not user_record:
            db.close()
            raise HTTPException(status_code=404,
                                detail=f"User with ID {user_id} not found.")

        # Check if the conversation ID already exists
        if conversations_table.find_one(conversation_id=conversation_id):
            db.close()
            raise HTTPException(status_code=409,
                                detail=f"Conversation with ID {conversation_id} already exists.")

        # Insert the new conversation
        conversations_table.insert(
            dict(conversation_id=conversation_id, name=name, history=json.dumps(dict()))
        )

        # Update the user's conversation IDs
        user_conversation_ids = json.loads(user_record["conversation_ids"])
        user_conversation_ids.append(conversation_id)
        users_table.update(
            dict(user_id=user_id, conversation_ids=json.dumps(user_conversation_ids)),
            ['user_id']
        )

        log.info(
            f"Added conversation with ID {conversation_id} to the 'conversations' table and linked it to user {user_id}.")

        db.commit()
        db.close()

    def get_user_conversations(self, user_id):
        """
        Get user's conversations as a dictionary {conversation_id: name}.

        Args:
            user_id (str): The user ID.

        Returns:
            dict: Dictionary of user's conversations {conversation_id: name}.
        """
        db = self.get()
        users_table = db["users"]
        conversations_table = db["conversations"]

        user_record = users_table.find_one(user_id=user_id)
        if user_record:
            user_conversation_ids = json.loads(user_record["conversation_ids"])
            user_conversations = {}

            for conversation_id in user_conversation_ids:
                conversation_record = conversations_table.find_one(conversation_id=conversation_id)
                if conversation_record:
                    user_conversations[conversation_id] = conversation_record["name"]

            db.close()
            return user_conversations

        log.warning(f"User with ID {user_id} not found.")
        db.close()
        return None

    def get_history(self, conversation_id):
        """
        Get the saved history for a conversation.

        Args:
            conversation_id (str): The conversation ID.

        Returns:
            dict or None: The saved history for the conversation or None if not found.
        """
        db = self.get()
        conversations_table = db["conversations"]

        conversation_record = conversations_table.find_one(conversation_id=conversation_id)
        if conversation_record:
            history = conversation_record["history"]
            db.close()
            return history

        log.warning(f"Conversation with ID {conversation_id} not found.")
        db.close()
        return None

    def update_history(self, conversation_id, new_history):
        """
        Update the history for a conversation.

        Args:
            conversation_id (str): The conversation ID.
            new_history (dict): The new history to be updated for the conversation.
        """
        db = self.get()
        conversations_table = db["conversations"]

        # Check if the conversation exists
        existing_record = conversations_table.find_one(conversation_id=conversation_id)

        if existing_record:
            # Update the history for the conversation
            conversations_table.update(
                dict(conversation_id=conversation_id, history=new_history),
                ['conversation_id']
            )
            log.info(f"Updated history for conversation with ID {conversation_id}.")

        db.commit()
        db.close()

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
