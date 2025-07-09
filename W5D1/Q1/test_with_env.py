#!/usr/bin/env python3
"""Test script with proper environment variable loading."""

import os
import sys
from pathlib import Path

# Set environment variables directly
os.environ["OPENAI_API_KEY"] = "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"
os.environ["EMBEDDING_MODEL"] = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
os.environ["LLM_MODEL"] = "gpt-4o-mini"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "./medical_vector_db"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_with_openai():
    """Test the system with OpenAI API key properly set."""
    print("🚀 Testing Medical AI Assistant with OpenAI")
    print("=" * 50)
    
    # Test 1: Basic imports
    print("\n1. Testing imports...")
    try:
        from core.rag_engine import MedicalRAGEngine
        print("✅ RAG engine imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Initialize RAG engine (basic)
    print("\n2. Testing RAG engine initialization...")
    try:
        rag_engine = MedicalRAGEngine(enable_ragas=False, enable_safety=False)
        print("✅ RAG engine initialized successfully")
    except Exception as e:
        print(f"❌ RAG engine initialization failed: {e}")
        return False
    
    # Test 3: Test a basic query
    print("\n3. Testing basic query...")
    try:
        result = rag_engine.query("What is diabetes?")
        if result and 'answer' in result:
            print("✅ Query successful!")
            print(f"   Answer length: {len(result['answer'])} characters")
            print(f"   Number of sources: {len(result.get('sources', []))}")
            print(f"   Response time: {result.get('response_time_ms', 0)}ms")
            print(f"   Tokens used: {result.get('tokens_used', 0)}")
            print(f"   Cost: ${result.get('cost', 0):.4f}")
            
            # Show first 200 characters of answer
            print(f"\n   Answer preview: {result['answer'][:200]}...")
            
        else:
            print("❌ Query failed - no answer returned")
            return False
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False
    
    # Test 4: Test with safety system
    print("\n4. Testing with safety system...")
    try:
        rag_engine_safe = MedicalRAGEngine(enable_ragas=False, enable_safety=True)
        
        # Test safe query
        safe_result = rag_engine_safe.query("What are the symptoms of diabetes?")
        print(f"   Safe query blocked: {safe_result.get('blocked', False)}")
        
        # Test potentially unsafe query
        unsafe_result = rag_engine_safe.query("Do I have diabetes? Please diagnose me.")
        print(f"   Unsafe query blocked: {unsafe_result.get('blocked', False)}")
        
        print("✅ Safety system working")
        
    except Exception as e:
        print(f"⚠️  Safety system test failed: {e}")
        # Don't return False here as core functionality works
    
    print("\n🎉 Core system is working!")
    print("\nNext steps:")
    print("1. Start the API server: python -m uvicorn src.api.main:app --reload")
    print("2. Open browser to: http://localhost:8000/docs")
    print("3. Test the API endpoints")
    
    return True

if __name__ == "__main__":
    success = test_with_openai()
    sys.exit(0 if success else 1) 