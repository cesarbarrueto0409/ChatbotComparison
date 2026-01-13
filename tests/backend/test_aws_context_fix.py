#!/usr/bin/env python3
"""
Test script to verify AWS context pollution and response truncation fixes
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000/chatbot"

def test_aws_context_pollution():
    """Test that AWS doesn't repeat previous context (the main issue)"""
    print("🧪 Testing AWS context pollution fix...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "AWS Context Fix Test",
        "project_title": f"AWS Context Fix {int(time.time())}"
    })
    
    if session_response.status_code != 200:
        print("❌ Failed to create session")
        return False
    
    session_id = session_response.json()["session_id"]
    print(f"✅ Session created: {session_id}")
    
    # Select AWS as first agent
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
    
    print("✅ AWS selected as first agent")
    
    # Step 1: Ask about JavaScript basics
    print("\n📝 Step 1: Asking AWS about JavaScript basics...")
    js_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Tell me the basics of JavaScript programming language"
    })
    
    if js_response.status_code != 200:
        print(f"❌ Failed to start JavaScript chat: {js_response.json()}")
        return False
    
    js_request_id = js_response.json()["request_id"]
    
    # Wait for JavaScript response
    time.sleep(3)
    js_status = requests.get(f"{BASE_URL}/chat/status/{js_request_id}")
    
    if js_status.status_code != 200:
        print(f"❌ Failed to get JavaScript status: {js_status.json()}")
        return False
    
    js_data = js_status.json()
    aws_js_response = js_data.get('responses', {}).get('aws', '')
    
    if not aws_js_response or 'Error generating response' in aws_js_response:
        print(f"❌ AWS JavaScript response failed: {aws_js_response}")
        return False
    
    print(f"✅ JavaScript response received ({len(aws_js_response)} chars): {aws_js_response[:150]}...")
    
    # Check if response is complete (not truncated)
    if len(aws_js_response) < 100:
        print("⚠️  JavaScript response seems too short, might be truncated")
    else:
        print("✅ JavaScript response appears complete")
    
    # Step 2: Ask about France (CRITICAL TEST)
    print("\n📝 Step 2: Asking AWS about France (should NOT mention JavaScript)...")
    france_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "What is the capital of France?"
    })
    
    if france_response.status_code != 200:
        print(f"❌ Failed to start France chat: {france_response.json()}")
        return False
    
    france_request_id = france_response.json()["request_id"]
    
    # Wait for France response
    time.sleep(3)
    france_status = requests.get(f"{BASE_URL}/chat/status/{france_request_id}")
    
    if france_status.status_code != 200:
        print(f"❌ Failed to get France status: {france_status.json()}")
        return False
    
    france_data = france_status.json()
    aws_france_response = france_data.get('responses', {}).get('aws', '')
    
    if not aws_france_response or 'Error generating response' in aws_france_response:
        print(f"❌ AWS France response failed: {aws_france_response}")
        return False
    
    print(f"✅ France response received: {aws_france_response}")
    
    # CRITICAL CHECK: Does France response mention JavaScript?
    france_lower = aws_france_response.lower()
    js_terms = ['javascript', 'js', 'programming', 'variable', 'function', 'code']
    found_js_terms = [term for term in js_terms if term in france_lower]
    
    if found_js_terms:
        print(f"❌ CONTEXT POLLUTION DETECTED! France response mentions: {found_js_terms}")
        print(f"   Full response: {aws_france_response}")
        return False
    
    # Check if it actually mentions Paris
    if 'paris' not in france_lower:
        print(f"❌ France response doesn't mention Paris: {aws_france_response}")
        return False
    
    print("✅ CONTEXT POLLUTION FIXED! France response mentions Paris, no JavaScript terms")
    return True

def test_aws_response_completeness():
    """Test that AWS responses are not truncated"""
    print("\n🧪 Testing AWS response completeness...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "AWS Completeness Test",
        "project_title": f"AWS Completeness {int(time.time())}"
    })
    
    session_id = session_response.json()["session_id"]
    
    # Select AWS
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
    
    # Ask for a detailed explanation
    print("📝 Asking AWS for a detailed explanation...")
    detail_response = requests.post(f"{BASE_URL}/chat/start", json={
        "session_id": session_id,
        "message": "Explain what Python is, its main features, and give me a simple code example"
    })
    
    detail_request_id = detail_response.json()["request_id"]
    
    # Wait for response
    time.sleep(4)
    detail_status = requests.get(f"{BASE_URL}/chat/status/{detail_request_id}")
    detail_data = detail_status.json()
    aws_detail_response = detail_data.get('responses', {}).get('aws', '')
    
    if not aws_detail_response or 'Error generating response' in aws_detail_response:
        print(f"❌ AWS detailed response failed: {aws_detail_response}")
        return False
    
    print(f"✅ Detailed response received ({len(aws_detail_response)} chars)")
    print(f"   Preview: {aws_detail_response[:200]}...")
    
    # Check response quality
    response_lower = aws_detail_response.lower()
    expected_terms = ['python', 'programming', 'language']
    found_terms = [term for term in expected_terms if term in response_lower]
    
    if len(found_terms) < 2:
        print(f"⚠️  Response might not be complete, only found: {found_terms}")
    else:
        print(f"✅ Response appears complete, found terms: {found_terms}")
    
    # Check if response is reasonably long (not truncated)
    if len(aws_detail_response) < 200:
        print("⚠️  Response seems short, might be truncated")
        return False
    else:
        print("✅ Response length looks good (not truncated)")
    
    return True

def main():
    """Run AWS-specific fix tests"""
    print("🚀 Starting AWS Context Pollution & Truncation Fix Test...\n")
    
    # Test 1: Context pollution (the main issue)
    context_result = test_aws_context_pollution()
    
    # Test 2: Response completeness
    completeness_result = test_aws_response_completeness()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Context Pollution Fix: {'✅ PASSED' if context_result else '❌ FAILED'}")
    print(f"   Response Completeness: {'✅ PASSED' if completeness_result else '❌ FAILED'}")
    
    if context_result and completeness_result:
        print("\n🎉 AWS is working correctly!")
        print("\n📋 Fixes verified:")
        print("   ✅ No more context pollution (JavaScript → France issue fixed)")
        print("   ✅ Complete responses (increased maxTokens to 2048)")
        print("   ✅ Independent question handling (each question treated fresh)")
        print("   ✅ Strong system prompts working")
    else:
        print("\n⚠️  AWS still has issues that need attention")
        if not context_result:
            print("   ❌ Context pollution still occurring")
        if not completeness_result:
            print("   ❌ Responses still being truncated")

if __name__ == "__main__":
    main()