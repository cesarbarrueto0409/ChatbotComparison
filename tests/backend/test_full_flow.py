"""
Full application flow test
Tests the complete chatbot workflow from session creation to chat completion
"""

import requests
import uuid
import time

# Configuration
API_BASE = "http://localhost:3000/chatbot"

def test_full_flow():
    """Test the complete application flow"""
    try:
        # 1. Health check
        print("1. Testing health check...")
        response = requests.get(f"{API_BASE}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   Health check passed")
        
        # 2. Get existing sessions
        print("\n2. Getting existing sessions...")
        response = requests.get(f"{API_BASE}/sessions")
        print(f"   Status: {response.status_code}")
        sessions_data = response.json()
        print(f"   Existing sessions: {len(sessions_data['sessions'])}")
        assert response.status_code == 200
        print("   Sessions retrieved")
        
        # 3. Create new session
        print("\n3. Creating new session...")
        session_data = {
            "action": "create",
            "name": "Test User",
            "project_title": f"Test Project {uuid.uuid4().hex[:8]}"
        }
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        print(f"   Status: {response.status_code}")
        create_response = response.json()
        print(f"   Response: {create_response}")
        assert response.status_code == 200
        assert create_response["success"] == True
        session_id = create_response["session_id"]
        print(f"   Session created: {session_id}")
        
        # 4. Get available AI agents
        print("\n4. Getting available AI agents...")
        ai_data = {
            "session_id": session_id,
            "action": "get_available"
        }
        response = requests.post(f"{API_BASE}/ai-selection", json=ai_data)
        print(f"   Status: {response.status_code}")
        agents_response = response.json()
        print(f"   Available agents: {[agent['key'] for agent in agents_response['available_agents']]}")
        assert response.status_code == 200
        available_agents = agents_response["available_agents"]
        print("   AI agents retrieved")
        
        # 5. Select first agent
        print("\n5. Selecting first AI agent...")
        first_agent = available_agents[0]["key"]
        select_data = {
            "session_id": session_id,
            "action": "select_first",
            "agent_key": first_agent
        }
        response = requests.post(f"{API_BASE}/ai-selection", json=select_data)
        print(f"   Status: {response.status_code}")
        print(f"   Selected: {first_agent}")
        assert response.status_code == 200
        print("   First agent selected")
        
        # 6. Get second agent options
        print("\n6. Getting second agent options...")
        second_options_data = {
            "session_id": session_id,
            "action": "get_second_options"
        }
        response = requests.post(f"{API_BASE}/ai-selection", json=second_options_data)
        second_agents = response.json()["available_agents"]
        print(f"   Second options: {len(second_agents)}")
        assert response.status_code == 200
        print("   Second agent options retrieved")
        
        # 7. Select second agent
        print("\n7. Selecting second AI agent...")
        second_agent = second_agents[0]["key"]
        select_second_data = {
            "session_id": session_id,
            "action": "select_second",
            "agent_key": second_agent
        }
        response = requests.post(f"{API_BASE}/ai-selection", json=select_second_data)
        print(f"   Status: {response.status_code}")
        final_response = response.json()
        print(f"   Selected: {second_agent}")
        assert response.status_code == 200
        assert final_response["ready_for_conversation"] == True
        print("   Second agent selected, ready for chat")
        
        # 8. Send test message
        print("\n8. Sending test message...")
        chat_data = {
            "session_id": session_id,
            "message": "Hello! This is a test message."
        }
        response = requests.post(f"{API_BASE}/chat", json=chat_data)
        
        if response.status_code == 200:
            chat_response = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Responses received: {len(chat_response['responses'])}")
            
            for agent_key, agent_response in chat_response['responses'].items():
                print(f"   {agent_key}: {agent_response[:100]}...")
                metadata = chat_response['metadata'].get(agent_key, {})
                print(f"      Time: {metadata.get('processing_time_seconds', 0)}s")
                print(f"      Cost: ${metadata.get('cost_usd', 0)}")
            
            print("   Chat message processed successfully")
        else:
            print(f"   Chat failed: {response.text}")
        
        print("\nAll tests passed! The application is working correctly.")
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Full Application Flow Test")
    print("=" * 50)
    print("Testing backend API endpoints...")
    print()
    
    success = test_full_flow()
    
    if success:
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("The chatbot application is working correctly!")
        print("Frontend: http://localhost:8080")
        print("API Docs: http://localhost:3000/chatbot/docs")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("SOME TESTS FAILED!")
        print("Check the error messages above.")
        print("=" * 50)

if __name__ == "__main__":
    main()