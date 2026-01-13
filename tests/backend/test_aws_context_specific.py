#!/usr/bin/env python3
"""
Test the specific AWS context issue: JavaScript -> France
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000/chatbot"

def test_specific_issue():
    """Test the specific JavaScript -> France issue"""
    print("🧪 Testing specific AWS context issue...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "AWS Context Issue Test",
        "project_title": f"AWS Context Issue {int(time.time())}"
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
    
    # Step 1: Ask about JavaScript
    print("\n📝 Step 1: Asking about JavaScript...")
    js_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Tell me the basics of JavaScript"
    })
    
    js_request_id = js_response.json()["request_id"]
    time.sleep(6)  # Wait longer for complex response
    
    js_status = requests.get(f"{BASE_URL}/chat/status/{js_request_id}")
    js_data = js_status.json()
    
    if 'aws' in js_data.get('responses', {}):
        aws_js = js_data['responses']['aws']
        print(f"AWS JavaScript response ({len(aws_js)} chars): {aws_js[:200]}...")
        
        if len(aws_js) < 50:
            print("⚠️  JavaScript response is very short")
        elif 'Error generating response' in aws_js:
            print("❌ JavaScript response has error")
        else:
            print("✅ JavaScript response looks good")
    else:
        print("❌ No AWS JavaScript response")
        return
    
    # Step 2: Ask about France
    print("\n📝 Step 2: Asking about France...")
    france_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "What is the capital of France?"
    })
    
    france_request_id = france_response.json()["request_id"]
    time.sleep(4)
    
    france_status = requests.get(f"{BASE_URL}/chat/status/{france_request_id}")
    france_data = france_status.json()
    
    if 'aws' in france_data.get('responses', {}):
        aws_france = france_data['responses']['aws']
        print(f"AWS France response: '{aws_france}'")
        
        # Check for context pollution
        france_lower = aws_france.lower()
        js_terms = ['javascript', 'programming', 'variable', 'function', 'code', 'language']
        found_terms = [term for term in js_terms if term in france_lower]
        
        if found_terms:
            print(f"❌ CONTEXT POLLUTION! Found terms: {found_terms}")
        else:
            print("✅ No context pollution detected")
        
        # Check if it mentions Paris
        if 'paris' in france_lower:
            print("✅ Correctly mentions Paris")
        else:
            print("❌ Doesn't mention Paris")
            
    else:
        print("❌ No AWS France response")

if __name__ == "__main__":
    test_specific_issue()