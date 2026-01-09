from abc import ABC, abstractmethod
from typing import List, Dict

"""Abstract class that defines the interface for AI agents."""
class AiAgent(ABC):
    @abstractmethod

    def respond(self, history: List[Dict[str, str]]) -> str:
        """Receive history's conversation and returns an answer"""
        pass
