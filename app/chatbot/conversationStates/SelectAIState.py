from app.chatbot.conversationStates.ConversationState import ConversationState
from app.chatbot.aiAgent.AiAgent import AiAgent
from app.chatbot.aiAgent.AzureAgent import AzureAgent
from app.chatbot.aiAgent.AwsAgent import AwsAgent
from typing import List, Optional, Dict, Type

class SelectAIState(ConversationState):
    """
    State for AI agent selection and comparison setup.
    Implements Strategy pattern for AI agent selection.
    """
    
    def __init__(self):
        # Registry of available AI agents (Factory pattern)
        self.available_agents: Dict[str, Type[AiAgent]] = {
            "azure": AzureAgent,
            "aws": AwsAgent,
            # Future agents can be easily added here
            # "openai": OpenAIAgent,
            # "anthropic": AnthropicAgent,
        }
        
        self.selected_agents: List[str] = []
        self.agent_instances: List[AiAgent] = []
    
    def handle(self, controller, user_input: str) -> str:
        """Handle method required by abstract base class (not used in new architecture)"""
        return "AI selection handled via API endpoints"
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """
        Get list of available AI agents with their information.
        
        Returns:
            List of dictionaries containing agent information
        """
        agents_info = []
        for agent_key, agent_class in self.available_agents.items():
            # Create temporary instance to get pricing info
            try:
                temp_instance = agent_class()
                pricing = temp_instance.get_pricing()
                
                agents_info.append({
                    "key": agent_key,
                    "name": agent_class.__name__,
                    "display_name": self._get_display_name(agent_key),
                    "description": self._get_agent_description(agent_key),
                    "input_price": pricing["input"],
                    "output_price": pricing["output"]
                })
            except Exception as e:
                print(f"Warning: Could not initialize {agent_class.__name__}: {e}")
                # Still add to list but with default values
                agents_info.append({
                    "key": agent_key,
                    "name": agent_class.__name__,
                    "display_name": self._get_display_name(agent_key),
                    "description": self._get_agent_description(agent_key),
                    "input_price": 0.0,
                    "output_price": 0.0
                })
        
        return agents_info
    
    def select_first_agent(self, agent_key: str) -> bool:
        """
        Select the first AI agent for comparison.
        
        Args:
            agent_key (str): Key of the agent to select
            
        Returns:
            bool: True if selection successful, False otherwise
        """
        if agent_key not in self.available_agents:
            return False
        
        # Allow re-selection of first agent
        self.selected_agents = [agent_key]
        return True
    
    def select_second_agent(self, agent_key: str) -> bool:
        """
        Select the second AI agent for comparison.
        
        Args:
            agent_key (str): Key of the agent to select
            
        Returns:
            bool: True if selection successful, False otherwise
        """
        if (agent_key not in self.available_agents or 
            len(self.selected_agents) != 1 or 
            agent_key == self.selected_agents[0]):
            return False
        
        self.selected_agents.append(agent_key)
        return True
    
    def get_available_second_agents(self) -> List[Dict[str, str]]:
        """
        Get available agents for second selection (excluding first selected).
        
        Returns:
            List of available agents excluding the first selected one
        """
        if not self.selected_agents:
            return []
        
        first_selected = self.selected_agents[0]
        all_agents = self.get_available_agents()
        
        return [agent for agent in all_agents if agent["key"] != first_selected]
    
    def create_agent_instances(self) -> List[AiAgent]:
        """
        Create instances of the selected AI agents.
        
        Returns:
            List of instantiated AI agents
        """
        if len(self.selected_agents) != 2:
            return []
        
        try:
            self.agent_instances = [
                self.available_agents[agent_key]() 
                for agent_key in self.selected_agents
            ]
            return self.agent_instances
        except Exception as e:
            print(f"Error creating agent instances: {e}")
            return []
    
    def get_selected_agents_info(self) -> List[Dict[str, str]]:
        """Get information about selected agents"""
        if len(self.selected_agents) != 2:
            return []
        
        all_agents = self.get_available_agents()
        return [
            agent for agent in all_agents 
            if agent["key"] in self.selected_agents
        ]
    
    def reset_selection(self):
        """Reset agent selection"""
        self.selected_agents = []
        self.agent_instances = []
    
    def _get_display_name(self, agent_key: str) -> str:
        """Get user-friendly display name for agent"""
        display_names = {
            "azure": "Azure OpenAI",
            "aws": "AWS Bedrock",
            "openai": "OpenAI GPT",
            "anthropic": "Anthropic Claude"
        }
        return display_names.get(agent_key, agent_key.title())
    
    def _get_agent_description(self, agent_key: str) -> str:
        """Get description for agent"""
        descriptions = {
            "azure": "Microsoft Azure OpenAI Service with GPT models",
            "aws": "Amazon Bedrock with Nova and Claude models",
            "openai": "Direct OpenAI API access",
            "anthropic": "Anthropic's Claude AI models"
        }
        return descriptions.get(agent_key, "AI Agent")