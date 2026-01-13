from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Define request and response schemas for the ChatBot API

class ChatRequest(BaseModel):
    session_id: str = Field(
        ..., 
        description="Unique identifier for the chat session",
        example="user-session-123",
        min_length=1,
        max_length=100
    )
    message: str = Field(
        ..., 
        description="User's message to the chatbot",
        example="Hello, how are you?",
        min_length=1,
        max_length=1000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-session-123",
                "message": "Hello, how can you help me today?"
            }
        }

class ChatResponse(BaseModel):
    responses: Dict[str, str] = Field(
        ...,
        description="Responses from AI agents"
    )
    metadata: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Metadata for each response including timing and cost"
    )
    user_info: Dict[str, str] = Field(
        ...,
        description="User information"
    )
    agent_info: List[Dict[str, Any]] = Field(
        ...,
        description="Information about the AI agents used"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "responses": {
                    "azure": "Hello! I'm doing well, thank you for asking.",
                    "aws": "Hi there! I'm functioning properly and ready to help."
                },
                "metadata": {
                    "azure": {
                        "processing_time_seconds": 1.234,
                        "cost_usd": 0.000123,
                        "model": "AzureAgent"
                    },
                    "aws": {
                        "processing_time_seconds": 0.987,
                        "cost_usd": 0.000098,
                        "model": "AwsAgent"
                    }
                },
                "user_info": {
                    "name": "John Doe",
                    "project_title": "AI Comparison Project",
                    "session_id": "user-session-123"
                },
                "agent_info": [
                    {
                        "key": "azure",
                        "display_name": "Azure OpenAI",
                        "description": "Microsoft Azure OpenAI Service"
                    }
                ]
            }
        }

# User Session Management Schemas
class UserSessionRequest(BaseModel):
    action: str = Field(
        ...,
        description="Action to perform: 'create' or 'select'",
        example="create"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID (required for 'select' action)",
        example="user-session-123"
    )
    name: Optional[str] = Field(
        None,
        description="User name (required for 'create' action)",
        example="John Doe"
    )
    project_title: Optional[str] = Field(
        None,
        description="Project title (required for 'create' action)",
        example="AI Comparison Project"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "action": "create",
                    "name": "John Doe",
                    "project_title": "AI Comparison Project"
                },
                {
                    "action": "select",
                    "session_id": "existing-session-123"
                }
            ]
        }

class UserSessionResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="Response message")

# AI Selection Schemas
class AISelectionRequest(BaseModel):
    session_id: str = Field(
        ...,
        description="Session ID",
        example="user-session-123"
    )
    action: str = Field(
        ...,
        description="Action: 'get_available', 'select_first', 'select_second', 'get_second_options'",
        example="get_available"
    )
    agent_key: Optional[str] = Field(
        None,
        description="Agent key to select",
        example="azure"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "session_id": "user-session-123",
                    "action": "get_available"
                },
                {
                    "session_id": "user-session-123",
                    "action": "select_first",
                    "agent_key": "azure"
                }
            ]
        }

class AISelectionResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    available_agents: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of available AI agents"
    )
    selected_agents: Optional[List[str]] = Field(
        None,
        description="List of selected agent keys"
    )
    ready_for_conversation: Optional[bool] = Field(
        False,
        description="Whether the session is ready for conversation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Available agents retrieved",
                "available_agents": [
                    {
                        "key": "azure",
                        "name": "AzureAgent",
                        "display_name": "Azure OpenAI",
                        "description": "Microsoft Azure OpenAI Service",
                        "input_price": 0.0015,
                        "output_price": 0.002
                    }
                ]
            }
        }