from typing import Dict, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.schemas import ChatRequest, ChatResponse, UserSessionRequest, UserSessionResponse, AISelectionRequest, AISelectionResponse
from app.chatbot.ChatbotController import ChatbotController, StateType
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(prefix="/chatbot")

# Global chatbot controllers for each session
chatbot_controllers: Dict[str, ChatbotController] = {}

def get_chatbot_controller(session_id: str) -> ChatbotController:
    """Get or create chatbot controller for session"""
    if session_id not in chatbot_controllers:
        chatbot_controllers[session_id] = ChatbotController()
    return chatbot_controllers[session_id]

@router.post("/sessions", response_model=UserSessionResponse)
def create_or_select_session(request: UserSessionRequest) -> UserSessionResponse:
    """Create new session or select existing one"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        controller = get_chatbot_controller(session_id)
        user_state = controller.get_current_state()
        
        if request.action == "create":
            # Create new session
            if not request.name or not request.project_title:
                raise HTTPException(status_code=400, detail="Name and project title required for new session")
            
            # Make sure we're using the correct state
            if controller.get_current_state_type() != StateType.SELECT_USER:
                controller.current_state_type = StateType.SELECT_USER
            
            user_state = controller.get_current_state()
            success = user_state.create_new_session(session_id, request.name, request.project_title)
            if not success:
                raise HTTPException(status_code=400, detail="Project title already exists")
            
            return UserSessionResponse(
                success=True,
                session_id=session_id,
                message="Session created successfully"
            )
            
        elif request.action == "select":
            # Select existing session
            if not request.session_id:
                raise HTTPException(status_code=400, detail="Session ID required for selection")
            
            # Make sure we're using the correct state
            if controller.get_current_state_type() != StateType.SELECT_USER:
                controller.current_state_type = StateType.SELECT_USER
            
            user_state = controller.get_current_state()
            success = user_state.select_existing_session(request.session_id)
            if not success:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return UserSessionResponse(
                success=True,
                session_id=request.session_id,
                message="Session selected successfully"
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in session management: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/sessions")
def get_all_sessions():
    """Get all available sessions"""
    try:
        # Create temporary controller to access user repository
        temp_controller = ChatbotController()
        user_state = temp_controller.states[StateType.SELECT_USER]
        sessions = user_state.get_all_sessions()
        
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/ai-selection", response_model=AISelectionResponse)
def select_ai_agents(request: AISelectionRequest) -> AISelectionResponse:
    """Select AI agents for comparison"""
    try:
        controller = get_chatbot_controller(request.session_id)
        
        # Transition to AI selection if needed
        if controller.get_current_state_type() == StateType.SELECT_USER:
            if not controller.transition_to_ai_selection():
                raise HTTPException(status_code=400, detail="No user selected for this session")
        elif controller.get_current_state_type() == StateType.ACTIVE_CONVERSATION:
            # Transition back from conversation to AI selection
            controller.current_state_type = StateType.SELECT_AI
            # Reset AI selection to allow re-selection
            ai_state = controller.get_current_state()
            ai_state.reset_selection()
        elif controller.get_current_state_type() != StateType.SELECT_AI:
            # Force transition to AI selection state
            controller.current_state_type = StateType.SELECT_AI
        
        ai_state = controller.get_current_state()
        
        if request.action == "get_available":
            # Get available agents
            agents = ai_state.get_available_agents()
            return AISelectionResponse(
                success=True,
                available_agents=agents,
                message="Available agents retrieved"
            )
            
        elif request.action == "select_first":
            # Select first agent
            if not request.agent_key:
                raise HTTPException(status_code=400, detail="Agent key required")
            
            success = ai_state.select_first_agent(request.agent_key)
            if not success:
                raise HTTPException(status_code=400, detail="Invalid agent selection")
            
            return AISelectionResponse(
                success=True,
                selected_agents=ai_state.selected_agents,
                message="First agent selected"
            )
            
        elif request.action == "select_second":
            # Select second agent
            if not request.agent_key:
                raise HTTPException(status_code=400, detail="Agent key required")
            
            success = ai_state.select_second_agent(request.agent_key)
            if not success:
                raise HTTPException(status_code=400, detail="Invalid second agent selection")
            
            # Transition to conversation state
            if controller.transition_to_conversation():
                return AISelectionResponse(
                    success=True,
                    selected_agents=ai_state.selected_agents,
                    ready_for_conversation=True,
                    message="Both agents selected, ready for conversation"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to initialize conversation")
                
        elif request.action == "get_second_options":
            # Get available options for second agent
            agents = ai_state.get_available_second_agents()
            return AISelectionResponse(
                success=True,
                available_agents=agents,
                message="Second agent options retrieved"
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI selection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Process chat message with selected AI agents"""
    try:
        controller = get_chatbot_controller(request.session_id)
        
        if not controller.is_ready_for_conversation():
            raise HTTPException(status_code=400, detail="Session not ready for conversation")
        
        session_data = controller.get_session_data()
        user = session_data["user"]
        agents = session_data["agents"]
        agent_info = session_data["agent_info"]
        
        # Get conversation service state and process message with threading
        conversation_service = controller.get_conversation_service()
        result = conversation_service.process_message_threaded(
            user=user,
            agents=agents,
            agent_info=agent_info,
            message=request.message
        )
        
        return ChatResponse(
            responses=result["responses"],
            metadata=result["metadata"],
            user_info=result["user_info"],
            agent_info=result["agent_info"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/chat/start")
def start_chat(request: ChatRequest):
    """Start processing chat message and return request ID for tracking"""
    try:
        controller = get_chatbot_controller(request.session_id)
        
        if not controller.is_ready_for_conversation():
            raise HTTPException(status_code=400, detail="Session not ready for conversation")
        
        session_data = controller.get_session_data()
        user = session_data["user"]
        agents = session_data["agents"]
        agent_info = session_data["agent_info"]
        
        # Get conversation service state and start processing message
        conversation_service = controller.get_conversation_service()
        request_id = conversation_service.start_message_processing(
            user=user,
            agents=agents,
            agent_info=agent_info,
            message=request.message
        )
        
        return {
            "request_id": request_id,
            "status": "processing",
            "message": "Message processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/chat/status/{request_id}")
def get_chat_status(request_id: str):
    """Get the current status of a chat processing request"""
    try:
        # Find the controller that has this request
        conversation_service = None
        for controller in chatbot_controllers.values():
            if controller.get_current_state_type() == StateType.ACTIVE_CONVERSATION:
                service = controller.get_conversation_service()
                if request_id in service.active_requests:
                    conversation_service = service
                    break
        
        if not conversation_service:
            raise HTTPException(status_code=404, detail="Request not found")
        
        status = conversation_service.get_request_status(request_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}

@router.get("/")
def chatbot_info():
    """Information about the chatbot service"""
    return {
        "service": "Enhanced ChatBot API",
        "version": "2.0.0",
        "features": [
            "Multi-user session management",
            "AI agent selection and comparison",
            "Real-time threaded responses",
            "Cost and performance tracking"
        ],
        "endpoints": {
            "sessions": "POST/GET /chatbot/sessions",
            "ai_selection": "POST /chatbot/ai-selection",
            "chat": "POST /chatbot/chat",
            "health": "GET /chatbot/health",
            "docs": "GET /chatbot/docs"
        }
    }