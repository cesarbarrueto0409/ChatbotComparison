import threading
import time
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.chatbot.conversationStates.ConversationState import ConversationState
from app.chatbot.aiAgent.AiAgent import AiAgent
from app.chatbot.memory.MongoMemory import MongoMemory
from app.chatbot.memory.RedisMemory import RedisMemory
from app.chatbot.User import User
import uuid

class ConversationServiceState(ConversationState):
    """
    State for handling active conversations with multiple AI agents.
    Implements Observer pattern for real-time response handling and threading.
    Combines the functionality of ConversationService with the State pattern.
    """
    
    def __init__(self):
        self.mongo = MongoMemory()
        self.redis = RedisMemory()
        self.response_callbacks: List[Callable] = []
        self.active_requests: Dict[str, Dict] = {}  # Track active requests
    
    def handle(self, controller, user_input: str) -> str:
        """Handle method required by abstract base class (legacy compatibility)"""
        return "Active conversation handled via API endpoints with threading"
    
    def add_response_callback(self, callback: Callable):
        """Add callback for real-time response updates"""
        self.response_callbacks.append(callback)
    
    def start_message_processing(
        self, 
        user: User, 
        agents: List[AiAgent], 
        agent_info: List[Dict], 
        message: str
    ) -> str:
        """
        Start processing message with multiple AI agents using threading.
        Returns a request ID for tracking progress.
        
        Args:
            user (User): User information
            agents (List[AiAgent]): List of AI agents
            agent_info (List[Dict]): Agent information
            message (str): User message
            
        Returns:
            str: Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        
        # Initialize request tracking
        self.active_requests[request_id] = {
            'status': 'processing',
            'responses': {},
            'metadata': {},
            'completed_agents': set(),
            'total_agents': len(agents),
            'user_info': {
                'name': user.name,
                'project_title': user.project_title,
                'session_id': user.session_id
            },
            'agent_info': agent_info
        }
        
        # Get conversation history
        history = self.redis.get_history(user.session_id)
        
        # Add user message to history with session info and request_id
        user_message = {
            "role": "user", 
            "content": message,
            "session_id": user.session_id,
            "request_id": request_id
        }
        history.append(user_message)
        self.redis.save_history(user.session_id, history)
        
        # Save user message to MongoDB with request_id
        self.mongo.save_message(
            session_id=user.session_id,
            role="user",
            content=message,
            user_name=user.name,
            project_title=user.project_title,
            request_id=request_id
        )
        
        # Process responses in parallel
        def process_agents():
            with ThreadPoolExecutor(max_workers=len(agents)) as executor:
                # Submit tasks for each agent
                future_to_agent = {
                    executor.submit(self._process_single_agent, agent, agent_info[i], history, user, request_id): 
                    (agent, agent_info[i]) for i, agent in enumerate(agents)
                }
                
                # Process completed responses as they arrive
                for future in as_completed(future_to_agent):
                    agent, info = future_to_agent[future]
                    try:
                        result = future.result()
                        agent_key = info["key"]
                        
                        # Update request tracking immediately when response is ready
                        self.active_requests[request_id]['responses'][agent_key] = result["response"]
                        self.active_requests[request_id]['metadata'][agent_key] = result["metadata"]
                        self.active_requests[request_id]['completed_agents'].add(agent_key)
                        
                        print(f"Agent {agent_key} completed in {result['metadata']['processing_time_seconds']} seconds")
                        
                        # Notify observers
                        for callback in self.response_callbacks:
                            try:
                                callback(request_id, agent_key, result)
                            except Exception as e:
                                print(f"Error in response callback: {e}")
                        
                        # Check if all agents completed
                        if len(self.active_requests[request_id]['completed_agents']) >= self.active_requests[request_id]['total_agents']:
                            self.active_requests[request_id]['status'] = 'completed'
                        
                    except Exception as e:
                        print(f"Error processing response from {info['display_name']}: {e}")
                        agent_key = info["key"]
                        self.active_requests[request_id]['responses'][agent_key] = f"Error: {str(e)}"
                        self.active_requests[request_id]['metadata'][agent_key] = {
                            "processing_time_seconds": 0,
                            "cost_usd": 0,
                            "error": True
                        }
                        self.active_requests[request_id]['completed_agents'].add(agent_key)
        
        # Start processing in background thread
        threading.Thread(target=process_agents, daemon=True).start()
        
        return request_id
    
    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the current status of a processing request.
        
        Args:
            request_id (str): Request ID
            
        Returns:
            Dict containing current status and any available responses
        """
        if request_id not in self.active_requests:
            return {"error": "Request not found"}
        
        request_data = self.active_requests[request_id].copy()
        
        # Clean up completed requests after some time
        if request_data['status'] == 'completed':
            # Keep for 5 minutes after completion
            if not hasattr(self.active_requests[request_id], 'completion_time'):
                self.active_requests[request_id]['completion_time'] = time.time()
            elif time.time() - self.active_requests[request_id]['completion_time'] > 300:
                del self.active_requests[request_id]
        
        return request_data
    
    def process_message_threaded(
        self, 
        user: User, 
        agents: List[AiAgent], 
        agent_info: List[Dict], 
        message: str
    ) -> Dict[str, Any]:
        """
        Process message with multiple AI agents using threading (legacy method for compatibility).
        
        Args:
            user (User): User information
            agents (List[AiAgent]): List of AI agents
            agent_info (List[Dict]): Agent information
            message (str): User message
            
        Returns:
            Dict containing responses and metadata
        """
        request_id = self.start_message_processing(user, agents, agent_info, message)
        
        # Wait for completion (with timeout)
        max_wait = 60  # 60 seconds max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_request_status(request_id)
            if status.get('status') == 'completed':
                return {
                    "responses": status["responses"],
                    "metadata": status["metadata"],
                    "user_info": status["user_info"],
                    "agent_info": status["agent_info"]
                }
            time.sleep(0.5)  # Check every 500ms
        
        # Timeout - return whatever we have
        status = self.get_request_status(request_id)
        return {
            "responses": status.get("responses", {}),
            "metadata": status.get("metadata", {}),
            "user_info": status.get("user_info", {}),
            "agent_info": status.get("agent_info", []),
            "timeout": True
        }
    
    def _process_single_agent(
        self, 
        agent: AiAgent, 
        agent_info: Dict, 
        history: List[Dict], 
        user: User,
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Process message with a single agent.
        
        Args:
            agent (AiAgent): AI agent instance
            agent_info (Dict): Agent information
            history (List[Dict]): Conversation history
            user (User): User information
            request_id (str): Request ID for tracking
            
        Returns:
            Dict containing response and metadata
        """
        start_time = time.time()
        
        try:
            # Generate response
            response = agent.respond(history)
            end_time = time.time()
            
            # Calculate metrics
            processing_time = round(end_time - start_time, 3)
            cost = self._calculate_cost(agent, response)
            
            # Save to MongoDB with request_id
            self.mongo.save_message(
                session_id=user.session_id,
                role="assistant",
                content=response,
                metadata={
                    "model": agent.__class__.__name__,
                    "processing_time_seconds": processing_time,
                    "cost_usd": cost,
                    "agent_key": agent_info["key"],
                    "request_id": request_id
                },
                user_name=user.name,
                project_title=user.project_title,
                request_id=request_id
            )
            
            return {
                "response": response,
                "metadata": {
                    "model": agent.__class__.__name__,
                    "processing_time_seconds": processing_time,
                    "cost_usd": cost,
                    "agent_key": agent_info["key"],
                    "display_name": agent_info["display_name"]
                }
            }
            
        except Exception as e:
            end_time = time.time()
            processing_time = round(end_time - start_time, 3)
            
            return {
                "response": f"Error generating response: {str(e)}",
                "metadata": {
                    "model": agent.__class__.__name__,
                    "processing_time_seconds": processing_time,
                    "cost_usd": 0,
                    "agent_key": agent_info["key"],
                    "display_name": agent_info["display_name"],
                    "error": True
                }
            }
    
    def _calculate_cost(self, agent: AiAgent, response: str) -> float:
        """Calculate response cost using agent's pricing"""
        try:
            pricing = agent.get_pricing()
            # Rough token estimation (1 token ≈ 4 characters)
            tokens = len(response) // 4
            input_cost = (tokens / 1000) * pricing["input"]
            output_cost = (tokens / 1000) * pricing["output"]
            return round(input_cost + output_cost, 6)
        except:
            return 0.0
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.redis.get_history(session_id)
    
    def clear_session_history(self, session_id: str):
        """Clear conversation history for a session"""
        self.redis.save_history(session_id, [])