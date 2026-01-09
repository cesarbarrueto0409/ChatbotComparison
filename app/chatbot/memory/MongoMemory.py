from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any
import os

class MongoMemory:
    def __init__(self):
        mongo_uri = os.getenv("URI_MONGODB") # Get MongoDB URI from environment variable
        if not mongo_uri:
            raise RuntimeError("URI_MONGODB environment variable is not set.")

        # Name of the database
        db_name = "chatbot_ai"

        client = MongoClient(mongo_uri)
        db = client[db_name]
        self.collection = db["conversation_messages"] #Name of the collection

    # Method to save a message to MongoDB
    def save_message(
        self,
        session_id: str, # Unique identifier for the chat session
        role: str, # Role of the message sender (user or assistant)
        content: str, # Content of the message
        metadata: Optional[Dict[str, Any]] = None # Additional metadata for the message (for example, model used [Azure, AWS, etc.])
    ):
        self.collection.insert_one({ # Insert the data into the collection
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        })