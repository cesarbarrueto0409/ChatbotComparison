from abc import ABC, abstractmethod

"""Abstract class that defines the interface for conversation states."""
class ConversationState(ABC):
    @abstractmethod
    def handle(self, controller, user_input: str) -> str:
        pass