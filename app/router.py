from typing import Dict
from fastapi import APIRouter
from app.chatbot.aiAgent.AwsAgent import AwsAgent
from app.chatbot.aiAgent.AzureAgent import AzureAgent
from app.schemas import ChatRequest
from app.chatbot.SessionsRegistry import get_controller


router: APIRouter = APIRouter(prefix="/chatbot")

@router.post("")
def chat(request: ChatRequest):
    agents = [AzureAgent(), AwsAgent()]
    controller = get_controller(request.session_id, agents)
    response = controller.handle_input(request.message)
    # Normalize to keys expected by the frontend (`azure`, `aws`)
    return {
        "azure": response.get("AzureAgent"),
        "aws": response.get("AwsAgent")
    }
