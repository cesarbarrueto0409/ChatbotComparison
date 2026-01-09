from pydantic import BaseModel

# Define request and response schemas for the ChatBot API

class ChatRequest(BaseModel):
    session_id: str # Unique identifier for the chat session
    message: str # User's message to the chatbot

class ChatResponse(BaseModel):
    response: str # Chatbot's response message