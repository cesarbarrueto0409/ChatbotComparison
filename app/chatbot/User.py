from typing import Optional
from datetime import datetime

class User:
    """
    Enhanced User class with name and project information.
    Follows the Entity pattern for domain modeling.
    """
    
    def __init__(self, session_id: str, name: str, project_title: str, created_at: Optional[datetime] = None):
        self.session_id = session_id  # Unique identifier for the session
        self.name = name  # User's name
        self.project_title = project_title  # Project title
        self.created_at = created_at or datetime.utcnow()  # Creation timestamp
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for database storage"""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "project_title": self.project_title,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            session_id=data["session_id"],
            name=data["name"],
            project_title=data["project_title"],
            created_at=data.get("created_at")
        )
    
    def __str__(self) -> str:
        return f"User(name='{self.name}', project='{self.project_title}', session='{self.session_id}')"
    
    def __repr__(self) -> str:
        return self.__str__()