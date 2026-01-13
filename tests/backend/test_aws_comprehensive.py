#!/usr/bin/env python3
"""
Comprehensive AWS test to ensure all issues are resolved
"""

import requests
import json
import time

BASE_URL = "http://localhost:3000/chatbot"

def comprehensive_aws_test():
    """Comprehensive test of AWS fixes"""
    print("🧪 Comprehensive AWS test...")
    
    # Create session
    session_response = requests.post(f"{BASE_URL}/sessions", json={
        "action": "create",
        "name": "Comprehensive AWS Test",
        "project_title": f"Comprehensive AWS {int(time.time())}"
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
    
    # Test sequence
    test_questions = [
        ("JavaScript basics", "Tell me the basics of JavaScript programming"),
        ("Capital of France", "What is the capital of France?"),
        ("Python programming", "Explain Python programming language"),
        ("Capital of Japan", "What is the capital of Japan?"),
        ("HTML basics", "What is HTML?"),
        ("Capital of Brazil", "What is the capital of Brazil?")
    ]
    
    results = []
    
    for i, (topic, question) in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {topic}")
        print(f"   Question: {question}")
        
        response = requests.post(f"{BASE_URL}/chat/start", json={
            "session_id": session_id,
            "message": question
        })
        
        request_id = response.json()["request_id"]
        time.sleep(4)
        
        status = requests.get(f"{BASE_URL}/chat/status/{request_id}")
        data = status.json()
        
        if 'aws' in data.get('responses', {}):
            aws_response = data['responses']['aws']
            aws_metadata = data.get('metadata', {}).get('aws', {})
            
            print(f"   AWS Response ({len(aws_response)} chars): {aws_response[:100]}...")
            print(f"   Processing time: {aws_metadata.get('processing_time_seconds', 0)}s")
            
            # Check for errors
            has_error = 'Error generating response' in aws_response
            is_empty = len(aws_response.strip()) == 0
            is_too_short = len(aws_response) < 20
            
            result = {
                'topic': topic,
                'question': question,
                'response': aws_response,
                'length': len(aws_response),
                'has_error': has_error,
                'is_empty': is_empty,
                'is_too_short': is_too_short,
                'processing_time': aws_metadata.get('processing_time_seconds', 0)
            }
            
            if has_error:
                print("   ❌ Has error")
            elif is_empty:
                print("   ❌ Empty response")
            elif is_too_short:
                print("   ⚠️  Very short response")
            else:
                print("   ✅ Good response")
            
            results.append(result)
        else:
            print("   ❌ No AWS response")
            results.append({
                'topic': topic,
                'question': question,
                'response': '',
                'length': 0,
                'has_error': True,
                'is_empty': True,
                'is_too_short': True,
                'processing_time': 0
            })
    
    # Analysis
    print(f"\n📊 Analysis of {len(results)} tests:")
    
    successful = [r for r in results if not r['has_error'] and not r['is_empty'] and not r['is_too_short']]
    errors = [r for r in results if r['has_error']]
    empty = [r for r in results if r['is_empty']]
    short = [r for r in results if r['is_too_short'] and not r['is_empty']]
    
    print(f"   ✅ Successful: {len(successful)}/{len(results)}")
    print(f"   ❌ Errors: {len(errors)}")
    print(f"   ❌ Empty: {len(empty)}")
    print(f"   ⚠️  Too short: {len(short)}")
    
    if successful:
        avg_length = sum(r['length'] for r in successful) / len(successful)
        avg_time = sum(r['processing_time'] for r in successful) / len(successful)
        print(f"   📏 Average response length: {avg_length:.0f} chars")
        print(f"   ⏱️  Average processing time: {avg_time:.2f}s")
    
    # Context pollution check
    print(f"\n🔍 Context pollution analysis:")
    programming_topics = ['JavaScript basics', 'Python programming', 'HTML basics']
    geography_topics = ['Capital of France', 'Capital of Japan', 'Capital of Brazil']
    
    programming_terms = ['javascript', 'python', 'html', 'programming', 'code', 'variable', 'function']
    
    pollution_detected = False
    for result in results:
        if result['topic'] in geography_topics:
            response_lower = result['response'].lower()
            found_terms = [term for term in programming_terms if term in response_lower]
            if found_terms:
                print(f"   ❌ Context pollution in '{result['topic']}': {found_terms}")
                pollution_detected = True
    
    if not pollution_detected:
        print("   ✅ No context pollution detected")
    
    # Summary
    success_rate = len(successful) / len(results) * 100
    print(f"\n🎯 Overall success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 AWS is working well!")
    elif success_rate >= 60:
        print("⚠️  AWS has some issues but mostly working")
    else:
        print("❌ AWS has significant issues")

if __name__ == "__main__":
    comprehensive_aws_test()