#!/usr/bin/env python3
"""
Simple test to debug AWS issues
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000/chatbot"

def simple_aws_test():
    """Simple AWS test"""
    print("🧪 Simple AWS test...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "Simple AWS Test",
        "project_title": f"Simple AWS Test {int(time.time())}"
    })
    
    session_id = session_response.json()["session_id"]
    print(f"Session: {session_id}")
    
    # Select agents
    requests.post(f"{BASE_URL}/ai-selection", json={
        "session_id": session_id,
        "action": "get_available"
    })
    
    requests.post(f"{BASE_URL}/ai-selection", json={
        "session_id": session_id,
        "action": "select_first",
        "agent_key": "aws"
    })
    
    requests.post(f"{BASE_URL}/ai-selection", json={
        "session_id": session_id,
        "action": "select_second",
        "agent_key": "azure"
    })
    
    # Simple question
    print("Asking simple question...")
    response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Hello, what is 2+2?"
    })
    
    request_id = response.json()["request_id"]
    print(f"Request ID: {request_id}")
    
    # Wait and check
    time.sleep(5)
    status = requests.get(f"{BASE_URL}/chat/status/{request_id}")
    data = status.json()
    
    print(f"Status: {data.get('status')}")
    print(f"Completed agents: {len(data.get('completed_agents', []))}")
    print(f"Responses: {list(data.get('responses', {}).keys())}")
    
    if 'aws' in data.get('responses', {}):
        aws_response = data['responses']['aws']
        print(f"AWS Response: '{aws_response}'")
        print(f"AWS Response length: {len(aws_response)}")
        
        if 'Error generating response' in aws_response:
            print("❌ AWS has error in response")
        elif len(aws_response.strip()) == 0:
            print("❌ AWS response is empty")
        else:
            print("✅ AWS responded successfully")
    else:
        print("❌ No AWS response found")
    
    if 'azure' in data.get('responses', {}):
        azure_response = data['responses']['azure']
        print(f"Azure Response: '{azure_response[:100]}...'")

if __name__ == "__main__":
    simple_aws_test()