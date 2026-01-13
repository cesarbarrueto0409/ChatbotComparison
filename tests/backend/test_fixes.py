"""
Test script for chatbot fixes
Tests specific functionality fixes including streaming chat and state transitions
"""

import requests
import uuid
import time

# Configuration
API_BASE = "http://localhost:3000/chatbot"

def test_session_creation():
    """Test session creation"""
    print("Testing session creation...")
    
    session_data = {
        "action": "create",
        "name": "Fix Test User",
        "project_title": f"Fix Test {uuid.uuid4().hex[:8]}"
    }
    
    response = requests.post(f"{API_BASE}/sessions", json=session_data)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print(f"Session created successfully: {result['session_id']}")
            return result["session_id"]
    
    print(f"Session creation failed: {response.json()}")
    return None

def test_ai_selection(session_id):
    """Test AI selection process"""
    print("Testing AI selection...")
    
    # Get available agents
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "get_available"
    })
    
    if response.status_code != 200:
        print("Failed to get available agents")
        return False
    
    agents = response.json()["available_agents"]
    
    if len(agents) < 2:
        print("Not enough agents available")
        return False
    
    # Select first agent
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "select_first",
        "agent_key": agents[0]["key"]
    })
    
    if response.status_code != 200:
        print("Failed to select first agent")
        return False
    
    # Get second agent options
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "get_second_options"
    })
    
    if response.status_code != 200:
        print("Failed to get second agent options")
        return False
    
    second_agents = response.json()["available_agents"]
    
    # Select second agent
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "select_second",
        "agent_key": second_agents[0]["key"]
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get("ready_for_conversation"):
            print("AI selection completed successfully")
            return True
    
    print("AI selection failed")
    return False

def test_state_transition_back(session_id):
    """Test transitioning back to AI selection"""
    print("Testing state transition back to AI selection...")
    
    # Try to go back to AI selection
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "get_available"
    })
    
    if response.status_code == 200:
        agents = response.json()["available_agents"]
        print(f"Successfully transitioned back. Available agents: {[agent['key'] for agent in agents]}")
        return True
    else:
        print(f"Error transitioning back: {response.json()}")
        return False

def test_streaming_chat(session_id):
    """Test streaming chat functionality"""
    print("Testing streaming chat...")
    
    # First, re-select agents to be ready for conversation
    print("Re-selecting agents for conversation...")
    
    # Get available agents
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "get_available"
    })
    
    if response.status_code != 200:
        print(f"Failed to get available agents: {response.json()}")
        return False
    
    agents = response.json()["available_agents"]
    
    # Select first agent
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "select_first",
        "agent_key": agents[0]["key"]
    })
    
    if response.status_code != 200:
        print(f"Failed to select first agent: {response.json()}")
        return False
    
    # Select second agent
    response = requests.post(f"{API_BASE}/ai-selection", json={
        "session_id": session_id,
        "action": "select_second",
        "agent_key": agents[1]["key"]
    })
    
    if response.status_code != 200:
        print(f"Failed to select second agent: {response.json()}")
        return False
    
    print("Agents re-selected successfully")
    
    # Start chat message
    response = requests.post(f"{API_BASE}/chat/start", json={
        "session_id": session_id,
        "message": "Hello! Please respond with a short greeting."
    })
    
    if response.status_code != 200:
        print("Failed to start chat message")
        return False
    
    request_id = response.json()["request_id"]
    print(f"Started chat with request ID: {request_id}")
    
    # Poll for responses
    max_polls = 30  # 30 seconds max
    poll_count = 0
    
    while poll_count < max_polls:
        response = requests.get(f"{API_BASE}/chat/status/{request_id}")
        
        if response.status_code != 200:
            print("Failed to get chat status")
            return False
        
        status = response.json()
        
        print(f"Poll {poll_count + 1}: Status = {status.get('status', 'unknown')}, "
              f"Completed = {len(status.get('completed_agents', []))}/{status.get('total_agents', 0)}")
        
        if status.get('status') == 'completed':
            print("Chat completed successfully!")
            
            # Print responses
            if status.get('responses'):
                for agent_key, agent_response in status['responses'].items():
                    if agent_response:
                        metadata = status.get('metadata', {}).get(agent_key, {})
                        processing_time = metadata.get('processing_time_seconds', 0)
                        print(f"Response from {agent_key} (took {processing_time}s): {agent_response[:100]}...")
            
            return True
        
        if status.get('status') == 'completed':
            break
        
        time.sleep(1)
        poll_count += 1
    
    print("Chat timed out")
    return False

def main():
    """Run all tests"""
    print("Starting chatbot fixes test...\n")
    
    # Test 1: Session creation
    session_id = test_session_creation()
    if not session_id:
        print("Session creation failed")
        return
    
    print(f"Session created: {session_id}")
    
    # Test 2: AI selection (including re-selection)
    if not test_ai_selection(session_id):
        print("AI selection failed")
        return
    
    print("AI selection working")
    
    # Test 3: State transition back
    if not test_state_transition_back(session_id):
        print("State transition back failed")
        return
    
    print("State transition back working")
    
    # Test 4: Streaming chat
    if not test_streaming_chat(session_id):
        print("Streaming chat failed")
        return
    
    print("Streaming chat working")
    
    print("\nAll tests passed! The fixes are working correctly.")

if __name__ == "__main__":
    main()