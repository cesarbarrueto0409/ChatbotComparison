from typing import Dict
from app.chatbot.ChatController import ChatController
from app.chatbot.aiAgent.AzureAgent import AiAgent

"""Global dictionary to hold session controllers
key: session_id (str)
value: ConversationController (class) instance"""
_controllers: Dict[str, ChatController] = {}

"""Function to get or create a ChatController for a given session_id and agent."""
def get_controller(session_id: str, agent: AiAgent) -> ChatController:
    if session_id not in _controllers: # If controller does not exist for the session_id, then create one
        _controllers[session_id] = ChatController(agent, session_id)
    return _controllers[session_id] # Return the existing or newly created controller