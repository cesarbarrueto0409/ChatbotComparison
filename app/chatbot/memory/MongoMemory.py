from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any, List
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
        metadata: Optional[Dict[str, Any]] = None, # Additional metadata for the message (for example, model used [Azure, AWS, etc.])
        user_name: Optional[str] = None, # User's name
        project_title: Optional[str] = None, # Project title
        request_id: Optional[str] = None # Request ID to track question-answer pairs
    ):
        document = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }
        
        # Add user information if provided
        if user_name:
            document["user_name"] = user_name
        if project_title:
            document["project_title"] = project_title
        if request_id:
            document["request_id"] = request_id
            
        self.collection.insert_one(document) # Insert the data into the collection
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        messages = self.collection.find(
            {"session_id": session_id}
        ).sort("created_at", 1)
        
        return list(messages)
    
    def get_smart_history(self, session_id: str, current_request_id: str) -> List[Dict[str, Any]]:
        """
        Get smart conversation history that:
        1. Includes important context (user introductions, names, etc.)
        2. Excludes already answered questions (by request_id)
        3. Limits to recent relevant messages
        """
        # Get all messages for this session
        all_messages = list(self.collection.find(
            {"session_id": session_id}
        ).sort("created_at", 1))
        
        if not all_messages:
            return []
        
        # Find important context messages (introductions, names, etc.)
        important_messages = []
        answered_request_ids = set()
        
        for msg in all_messages:
            # Track answered request IDs
            if msg.get("request_id") and msg["role"] == "assistant":
                answered_request_ids.add(msg["request_id"])
            
            # Identify important context messages
            content_lower = msg["content"].lower()
            is_important = (
                msg["role"] == "user" and (
                    "my name is" in content_lower or
                    "i am" in content_lower or
                    "call me" in content_lower or
                    "i'm" in content_lower
                )
            )
            
            if is_important:
                important_messages.append(msg)
        
        # Get recent messages (last 6) excluding already answered questions
        recent_messages = []
        for msg in all_messages[-12:]:  # Look at last 12 messages
            # Skip user questions that were already answered
            if (msg["role"] == "user" and 
                msg.get("request_id") and 
                msg["request_id"] in answered_request_ids and
                msg["request_id"] != current_request_id):
                continue
            
            # Skip assistant responses to old questions
            if (msg["role"] == "assistant" and 
                msg.get("request_id") and 
                msg["request_id"] != current_request_id):
                continue
            
            recent_messages.append(msg)
        
        # Combine important context + recent messages
        combined_messages = important_messages + recent_messages[-6:]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_messages = []
        for msg in combined_messages:
            msg_id = str(msg.get("_id"))
            if msg_id not in seen:
                seen.add(msg_id)
                unique_messages.append(msg)
        
        # Sort by creation time
        unique_messages.sort(key=lambda x: x["created_at"])
        
        return unique_messages
    
    def get_user_conversations(self, user_name: str, project_title: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user and project"""
        messages = self.collection.find({
            "user_name": user_name,
            "project_title": project_title
        }).sort("created_at", 1)
        
        return list(messages)