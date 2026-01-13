from abc import ABC, abstractmethod
from typing import List, Dict
import os

"""Abstract class that defines the interface for AI agents."""
class AiAgent(ABC):
    def __init__(self):
        # Initialize pricing attributes that will be set by subclasses
        self.input_price_per_1k_tokens = 0.0
        self.output_price_per_1k_tokens = 0.0

    @abstractmethod
    def respond(self, history: List[Dict[str, str]]) -> str:
        """Receive history's conversation and returns an answer"""
        pass

    def get_pricing(self) -> Dict[str, float]:
        """Return pricing information for this agent"""
        return {
            "input": self.input_price_per_1k_tokens,
            "output": self.output_price_per_1k_tokens
        }
