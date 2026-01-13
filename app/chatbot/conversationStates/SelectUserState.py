from app.chatbot.conversationStates.ConversationState import ConversationState
from app.chatbot.User import User
from app.chatbot.repositories.UserRepository import UserRepository
from typing import Optional

class SelectUserState(ConversationState):
    """
    State for user selection and session management.
    Handles user creation and session selection.
    """
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.selected_user: Optional[User] = None
    
    def handle(self, controller, user_input: str) -> str:
        """Handle method required by abstract base class (not used in new architecture)"""
        return "User selection handled via API endpoints"
    
    def create_new_session(self, session_id: str, name: str, project_title: str) -> bool:
        """
        Create a new user session.
        
        Args:
            session_id (str): Unique session identifier
            name (str): User's name
            project_title (str): Project title
            
        Returns:
            bool: True if session created successfully, False otherwise
        """
        # Check if project title already exists
        if self.user_repository.user_exists(project_title=project_title):
            return False
        
        # Create new user
        user = User(session_id=session_id, name=name, project_title=project_title)
        success = self.user_repository.save_user(user)
        
        if success:
            self.selected_user = user
        
        return success
    
    def select_existing_session(self, session_id: str) -> bool:
        """
        Select an existing user session.
        
        Args:
            session_id (str): Session identifier to select
            
        Returns:
            bool: True if session found and selected, False otherwise
        """
        user = self.user_repository.find_by_session_id(session_id)
        if user:
            self.selected_user = user
            return True
        return False
    
    def get_all_sessions(self) -> list:
        """Get all available user sessions"""
        users = self.user_repository.get_all_users()
        return [
            {
                "session_id": user.session_id,
                "name": user.name,
                "project_title": user.project_title,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
    
    def get_selected_user(self) -> Optional[User]:
        """Get the currently selected user"""
        return self.selected_user
    
    def validate_project_title(self, project_title: str) -> bool:
        """Check if project title is available"""
        return not self.user_repository.user_exists(project_title=project_title)