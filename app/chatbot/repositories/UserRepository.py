from typing import List, Optional
from pymongo import MongoClient
from app.chatbot.User import User
import os

class UserRepository:
    """
    Repository pattern for User data access.
    Handles all database operations related to users.
    """
    
    def __init__(self):
        mongo_uri = os.getenv("URI_MONGODB")
        if not mongo_uri:
            raise RuntimeError("URI_MONGODB environment variable is not set.")
        
        client = MongoClient(mongo_uri)
        db = client["chatbot_ai"]
        self.collection = db["users"]
        
        # Create compound index for session_id and project_title
        self.collection.create_index([("session_id", 1), ("project_title", 1)], unique=True)
    
    def save_user(self, user: User) -> bool:
        """Save or update a user in the database"""
        try:
            self.collection.replace_one(
                {"session_id": user.session_id},
                user.to_dict(),
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def find_by_session_id(self, session_id: str) -> Optional[User]:
        """Find user by session ID"""
        data = self.collection.find_one({"session_id": session_id})
        return User.from_dict(data) if data else None
    
    def find_by_project_title(self, project_title: str) -> Optional[User]:
        """Find user by project title"""
        data = self.collection.find_one({"project_title": project_title})
        return User.from_dict(data) if data else None
    
    def get_all_users(self) -> List[User]:
        """Get all users from the database"""
        users_data = self.collection.find().sort("created_at", -1)
        return [User.from_dict(data) for data in users_data]
    
    def delete_user(self, session_id: str) -> bool:
        """Delete user by session ID"""
        try:
            result = self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def user_exists(self, session_id: str = None, project_title: str = None) -> bool:
        """Check if user exists by session_id or project_title"""
        query = {}
        if session_id:
            query["session_id"] = session_id
        if project_title:
            query["project_title"] = project_title
        
        return self.collection.find_one(query) is not None