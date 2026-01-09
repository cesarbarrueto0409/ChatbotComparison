import os
from openai import AzureOpenAI

from app.chatbot.aiAgent.AiAgent import AiAgent

"""AI agent implementation for Azure OpenAI Service."""
class AzureAgent(AiAgent):
    #Constructor to initialize Azure OpenAI client with necessary configurations
    def __init__(self) -> None:
        api_key = os.getenv("AZURE_OPENAI_KEY") # Get API key from environment variables
        if not api_key:
            raise RuntimeError("AZURE_OPENAI_KEY is not set in environment variables.")

        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Get endpoint from environment variables
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # Get deployment name from environment variables
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION") # Get API version from environment variables
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version
        )

    # Method to respond to user input based on conversation history
    def respond(self, history: list) -> str: # parameter history is a list of messages 
        completion = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=history, # Pass the conversation history to the model
            temperature=0.7
        )
        return completion.choices[0].message.content # Return the generated response content
