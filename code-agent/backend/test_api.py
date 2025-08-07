#!/usr/bin/env python3
"""
Simple test script for the Code Agent Backend API
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoints"""
    print("🔍 Testing health endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"   GET / - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print(f"   GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Health Status: {health_data['status']}")
            print(f"   OpenAI Key: {'✅' if health_data['openai_key_configured'] else '❌'}")
            print(f"   Graph Init: {'✅' if health_data['graph_initialized'] else '❌'}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend. Is the server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\\n💬 Testing chat endpoint...")
    
    test_messages = [
        "Hello, can you help me with Python?",
        "Explain what a function is",
        "Write a simple hello world function"
    ]
    
    for i, message in enumerate(test_messages):
        try:
            print(f"\\n   Test {i+1}: {message}")
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Conversation ID: {data['conversation_id'][:8]}...")
                print(f"   Response Preview: {data['response'][:100]}...")
                print(f"   Status: {data['status']}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Code Agent Backend API Test")
    print("=" * 40)
    
    # Test health first
    if not test_health():
        print("\\n❌ Health check failed. Please start the backend server first.")
        print("   Run: ./start.sh")
        sys.exit(1)
    
    # Test chat functionality
    test_chat()
    
    print("\\n" + "=" * 40)
    print("✅ API tests completed!")
    print("\\n📚 For more detailed API docs, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
