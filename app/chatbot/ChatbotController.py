from enum import Enum
from typing import Optional, Dict, Any, List
from app.chatbot.conversationStates.SelectUserState import SelectUserState
from app.chatbot.conversationStates.SelectAIState import SelectAIState
from app.chatbot.conversationStates.ConversationServiceState import ConversationServiceState
from app.chatbot.memory.MongoMemory import MongoMemory
from app.chatbot.memory.RedisMemory import RedisMemory

class StateType(Enum):
    """Enumeration of available conversation states"""
    SELECT_USER = "select_user"
    SELECT_AI = "select_ai"
    ACTIVE_CONVERSATION = "active_conversation"

class ChatbotController:
    """
    Main Chatbot Controller implementing State pattern.
    Coordinates transitions between different conversation states and manages conversation flow.
    """
    
    def __init__(self):
        # State management
        self.current_state_type = StateType.SELECT_USER
        self.states: Dict[StateType, Any] = {
            StateType.SELECT_USER: SelectUserState(),
            StateType.SELECT_AI: SelectAIState(),
            StateType.ACTIVE_CONVERSATION: ConversationServiceState()
        }
        self.session_data: Dict[str, Any] = {}
        
        # Memory systems
        self.redis = RedisMemory()
        self.mongo = MongoMemory()
    
    # ==================== STATE MANAGEMENT METHODS ====================
    
    def get_current_state(self):
        """Get the current active state"""
        return self.states[self.current_state_type]
    
    def get_current_state_type(self) -> StateType:
        """Get the current state type"""
        return self.current_state_type
    
    def transition_to_ai_selection(self) -> bool:
        """Transition from user selection to AI selection"""
        if self.current_state_type == StateType.SELECT_USER:
            user_state = self.states[StateType.SELECT_USER]
            selected_user = user_state.get_selected_user()
            
            if selected_user:
                self.session_data["user"] = selected_user
                self.current_state_type = StateType.SELECT_AI
                return True
        return False
    
    def transition_to_conversation(self) -> bool:
        """Transition from AI selection to active conversation"""
        if self.current_state_type == StateType.SELECT_AI:
            ai_state = self.states[StateType.SELECT_AI]
            
            if len(ai_state.selected_agents) == 2:
                agents = ai_state.create_agent_instances()
                if agents:
                    self.session_data["agents"] = agents
                    self.session_data["agent_info"] = ai_state.get_selected_agents_info()
                    self.current_state_type = StateType.ACTIVE_CONVERSATION
                    return True
        return False
    
    def transition_back_to_ai_selection(self) -> bool:
        """Transition back from conversation to AI selection"""
        if self.current_state_type == StateType.ACTIVE_CONVERSATION:
            self.current_state_type = StateType.SELECT_AI
            # Reset AI selection to allow re-selection
            ai_state = self.states[StateType.SELECT_AI]
            ai_state.reset_selection()
            return True
        return False
    
    def reset_to_user_selection(self):
        """Reset to user selection state"""
        self.current_state_type = StateType.SELECT_USER
        self.session_data = {}
        
        # Reset all states
        for state in self.states.values():
            if hasattr(state, 'reset_selection'):
                state.reset_selection()
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data"""
        return self.session_data.copy()
    
    def set_session_data(self, key: str, value: Any):
        """Set session data"""
        self.session_data[key] = value
    
    def is_ready_for_conversation(self) -> bool:
        """Check if all requirements are met for conversation"""
        return (
            self.current_state_type == StateType.ACTIVE_CONVERSATION and
            "user" in self.session_data and
            "agents" in self.session_data and
            len(self.session_data.get("agents", [])) == 2
        )
    
    # ==================== UTILITY METHODS ====================
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.redis.get_history(session_id)
    
    def save_message(self, session_id: str, role: str, content: str, metadata: Dict = None, user_name: str = None, project_title: str = None):
        """Save a message to both Redis and MongoDB"""
        # Save to Redis (for quick access)
        history = self.redis.get_history(session_id)
        history.append({"role": role, "content": content})
        self.redis.save_history(session_id, history)
        
        # Save to MongoDB (for persistence)
        self.mongo.save_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
            user_name=user_name,
            project_title=project_title
        )
    
    def clear_session_data(self, session_id: str):
        """Clear all data for a specific session"""
        # Clear Redis history
        self.redis.save_history(session_id, [])
        
        # Reset session data if it matches current session
        if self.session_data.get("user", {}).get("session_id") == session_id:
            self.reset_to_user_selection()
    
    def get_conversation_service(self) -> ConversationServiceState:
        """Get the conversation service state for direct access to threading functionality"""
        return self.states[StateType.ACTIVE_CONVERSATION]
    
    def __str__(self) -> str:
        """String representation of the controller state"""
        return f"ChatbotController(state={self.current_state_type.value}, session_data_keys={list(self.session_data.keys())})"
    
    def __repr__(self) -> str:
        """Detailed representation of the controller"""
        return self.__str__()