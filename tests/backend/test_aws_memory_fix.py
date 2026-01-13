#!/usr/bin/env python3
"""
Test script to verify AWS memory and context management fixes
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000/chatbot"

def test_aws_memory_and_context():
    """Test AWS memory retention and context management"""
    print("🧪 Testing AWS memory retention and context management...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "AWS Memory Test",
        "project_title": f"AWS Memory Test {int(time.time())}"
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
    
    # Step 1: Introduce name
    print("\n📝 Step 1: Introducing name to AWS...")
    name_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Hello! My name is Alice. Please remember my name."
    })
    
    name_request_id = name_response.json()["request_id"]
    time.sleep(3)
    
    name_status = requests.get(f"{BASE_URL}/chat/status/{name_request_id}")
    name_data = name_status.json()
    
    if 'aws' in name_data.get('responses', {}):
        aws_name_response = name_data['responses']['aws']
        print(f"AWS name response: {aws_name_response}")
        
        if 'alice' in aws_name_response.lower():
            print("✅ AWS acknowledged the name")
        else:
            print("⚠️  AWS didn't clearly acknowledge the name")
    
    # Step 2: Ask about JavaScript (should be complete)
    print("\n📝 Step 2: Asking about JavaScript basics (should be complete)...")
    js_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Tell me the basics of JavaScript programming language with examples"
    })
    
    js_request_id = js_response.json()["request_id"]
    time.sleep(6)  # Wait longer for complex response
    
    js_status = requests.get(f"{BASE_URL}/chat/status/{js_request_id}")
    js_data = js_status.json()
    
    if 'aws' in js_data.get('responses', {}):
        aws_js_response = js_data['responses']['aws']
        print(f"AWS JavaScript response ({len(aws_js_response)} chars): {aws_js_response[:200]}...")
        
        if len(aws_js_response) < 500:
            print("❌ JavaScript response seems truncated (too short)")
        elif 'javascript' in aws_js_response.lower():
            print("✅ JavaScript response appears complete")
        else:
            print("⚠️  JavaScript response might be incomplete")
    
    # Step 3: Ask about something else (should not mention JavaScript)
    print("\n📝 Step 3: Asking about Python (should not mention JavaScript)...")
    python_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "What is Python programming language?"
    })
    
    python_request_id = python_response.json()["request_id"]
    time.sleep(4)
    
    python_status = requests.get(f"{BASE_URL}/chat/status/{python_request_id}")
    python_data = python_status.json()
    
    if 'aws' in python_data.get('responses', {}):
        aws_python_response = python_data['responses']['aws']
        print(f"AWS Python response: {aws_python_response}")
        
        # Check for JavaScript contamination
        if 'javascript' in aws_python_response.lower():
            print("❌ Context pollution: Python response mentions JavaScript")
        else:
            print("✅ No context pollution: Python response is clean")
    
    # Step 4: Ask if it remembers the name (CRITICAL TEST)
    print("\n📝 Step 4: Testing memory - asking if AWS remembers the name...")
    memory_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Do you remember my name? What is my name?"
    })
    
    memory_request_id = memory_response.json()["request_id"]
    time.sleep(3)
    
    memory_status = requests.get(f"{BASE_URL}/chat/status/{memory_request_id}")
    memory_data = memory_status.json()
    
    if 'aws' in memory_data.get('responses', {}):
        aws_memory_response = memory_data['responses']['aws']
        print(f"AWS memory response: {aws_memory_response}")
        
        if 'alice' in aws_memory_response.lower():
            print("✅ MEMORY WORKING: AWS remembers the name Alice!")
        else:
            print("❌ MEMORY FAILED: AWS doesn't remember the name")
    
    # Step 5: Ask about JavaScript again (should not repeat the full explanation)
    print("\n📝 Step 5: Asking about JavaScript again (should not repeat full explanation)...")
    js2_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Tell me the basics of JavaScript programming language with examples"
    })
    
    js2_request_id = js2_response.json()["request_id"]
    time.sleep(4)
    
    js2_status = requests.get(f"{BASE_URL}/chat/status/{js2_request_id}")
    js2_data = js2_status.json()
    
    if 'aws' in js2_data.get('responses', {}):
        aws_js2_response = js2_data['responses']['aws']
        print(f"AWS JavaScript repeat response ({len(aws_js2_response)} chars): {aws_js2_response[:200]}...")
        
        # Compare with first JavaScript response
        if 'aws' in js_data.get('responses', {}):
            first_js = js_data['responses']['aws']
            if len(aws_js2_response) < len(first_js) * 0.5:
                print("✅ SMART CONTEXT: Second JavaScript response is shorter (avoiding repetition)")
            elif aws_js2_response == first_js:
                print("⚠️  Identical responses - might be repeating")
            else:
                print("✅ Different but complete response")

def test_javascript_completeness():
    """Specific test for JavaScript response completeness"""
    print("\n🧪 Testing JavaScript response completeness specifically...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "JS Completeness Test",
        "project_title": f"JS Test {int(time.time())}"
    })
    
    session_id = session_response.json()["session_id"]
    
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
    
    # Ask about JavaScript with detailed request
    print("📝 Asking for detailed JavaScript explanation...")
    js_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Explain JavaScript basics including variables, functions, data types, and provide code examples for each concept"
    })
    
    js_request_id = js_response.json()["request_id"]
    time.sleep(8)  # Wait longer for detailed response
    
    js_status = requests.get(f"{BASE_URL}/chat/status/{js_request_id}")
    js_data = js_status.json()
    
    if 'aws' in js_data.get('responses', {}):
        aws_js = js_data['responses']['aws']
        azure_js = js_data['responses'].get('azure', '')
        
        print(f"AWS JavaScript response length: {len(aws_js)} chars")
        print(f"Azure JavaScript response length: {len(azure_js)} chars")
        print(f"AWS response preview: {aws_js[:300]}...")
        
        # Check for completeness indicators
        js_lower = aws_js.lower()
        completeness_indicators = [
            'variable' in js_lower,
            'function' in js_lower,
            'data type' in js_lower or 'datatype' in js_lower,
            'example' in js_lower,
            len(aws_js) > 800  # Should be substantial
        ]
        
        complete_count = sum(completeness_indicators)
        print(f"Completeness indicators: {complete_count}/5")
        
        if complete_count >= 4:
            print("✅ JavaScript response appears complete")
        else:
            print("❌ JavaScript response appears incomplete or truncated")
            
        # Check if it ends abruptly
        if aws_js.endswith('...') or len(aws_js) < 500:
            print("⚠️  Response might be truncated")

def main():
    """Run AWS memory and context tests"""
    print("🚀 Starting AWS Memory & Context Management Test...\n")
    
    # Test 1: Memory and context management
    test_aws_memory_and_context()
    
    # Test 2: JavaScript completeness
    test_javascript_completeness()
    
    print("\n📊 Test Summary:")
    print("   🧠 Memory test: Check if AWS remembers names across questions")
    print("   🔄 Context test: Check if AWS avoids repeating previous answers")
    print("   📝 Completeness test: Check if JavaScript responses are complete")
    print("   🚫 Pollution test: Check if AWS doesn't mix topics inappropriately")

if __name__ == "__main__":
    main()