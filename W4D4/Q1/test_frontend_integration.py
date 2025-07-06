#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration
"""
import requests
import json
import os

def test_backend_health():
    """Test if backend is healthy"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200 and "HR Knowledge Assistant" in response.text:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend accessibility failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_document_upload():
    """Test document upload through backend"""
    # Create a test document
    test_content = """
    HR Policy Document
    
    Vacation Policy:
    All employees receive 15 vacation days per year.
    Additional days may be earned based on tenure.
    
    Remote Work Policy:
    Employees may work remotely up to 3 days per week.
    Prior approval from manager is required.
    """
    
    with open("test_hr_doc.txt", "w") as f:
        f.write(test_content)
    
    try:
        with open("test_hr_doc.txt", "rb") as f:
            files = {"file": f}
            response = requests.post("http://localhost:8000/upload-doc", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document upload successful: {data['chunks_indexed']} chunks indexed")
            return True
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists("test_hr_doc.txt"):
            os.remove("test_hr_doc.txt")

def test_chat_functionality():
    """Test chat functionality through backend"""
    try:
        payload = {"query": "How many vacation days do employees get?"}
        response = requests.post("http://localhost:8000/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat functionality working")
            print(f"   Answer: {data['answer'][:100]}...")
            if data.get('citations'):
                print(f"   Citations: {len(data['citations'])} sources")
            return True
        else:
            print(f"❌ Chat functionality failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat functionality error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Testing HR Knowledge Assistant Integration\n")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("Document Upload", test_document_upload),
        ("Chat Functionality", test_chat_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your HR Knowledge Assistant is ready to use.")
        print("\n📋 Quick Start:")
        print("1. Backend: http://localhost:8000")
        print("2. Frontend: http://localhost:3000")
        print("3. Upload documents and start asking questions!")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 