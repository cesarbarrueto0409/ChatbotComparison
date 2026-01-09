from typing import List
from app.chatbot.memory.MongoMemory import MongoMemory
from app.chatbot.memory.RedisMemory import RedisMemory
from app.chatbot.conversationStates.ActiveConversationState import ActiveConversationState
from app.chatbot.conversationStates.ConversationState import ConversationState
from app.chatbot.aiAgent.AiAgent import AiAgent

"""Controller to manage conversation flow and states between user and AI agents."""
class ChatController:
    def __init__(self, agents: List[AiAgent], session_id: str) -> None:
        self.agents = agents # List of AI agents involved in the conversation
        self.session_id = session_id # Unique identifier for the chat session
        # Initialize memory systems
        self.redis = RedisMemory()
        self.mongo = MongoMemory()
        # Set initial conversation state
        self.state: ConversationState = ActiveConversationState()

    # Method to handle user input and generate responses from AI agents, returns a dictionary of responses from each agent
    def handle_input(self, user_input: str) -> dict:
        history = self.redis.get_history(self.session_id)

        # Append user input to conversation history (redis and mongo)
        history.append({"role": "user", "content": user_input})
        self.redis.save_history(self.session_id, history)
        self.mongo.save_message(self.session_id, "user", user_input)

        responses = {} # Dictionary to hold responses from each agent

        # Iterate through each AI agent to get their responses
        for agent in self.agents:
            model_name = agent.__class__.__name__
            answer = agent.respond(history)

            responses[model_name] = answer

            # Append agent response to conversation history (redis and mongo)
            self.mongo.save_message(
                session_id=self.session_id,
                role="assistant",
                content=answer,
                metadata={"model": model_name}
            )
        return responses # Return the dictionary of responses
