#!/usr/bin/env python3
"""Simple test script to verify the backend setup works."""

import os
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from backend import config
        from backend.models import DocumentChunk
        from backend.providers import OpenAIProvider
        from backend.vector_store import SimpleVectorStore
        from backend.ingestion import ingest_document
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without OpenAI API."""
    try:
        # Test vector store
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SimpleVectorStore(dim=4, path=tmp_dir)
            
            # Test adding dummy embeddings
            embeddings = [[0.1, 0.2, 0.3, 0.4]]  # 4 dim for testing
            metadata = [{"source": "test", "chunk_index": "0"}]
            store.add(embeddings, metadata)
            
            # Test search
            results = store.search([0.1, 0.2, 0.3, 0.4], k=1)
            assert len(results) == 1
            
        print("✓ Vector store functionality works")
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_text_file_ingestion():
    """Test text file ingestion."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for HR onboarding.\n")
            f.write("It contains information about company policies.\n")
            f.write("New employees should read this carefully.")
            temp_path = f.name
        
        try:
            chunks = ingest_document(temp_path)
            assert len(chunks) > 0
            assert all(isinstance(chunk.text, str) for chunk in chunks)
            assert all(chunk.metadata.get("source_path") for chunk in chunks)
            print("✓ Text file ingestion works")
            return True
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"✗ Text file ingestion failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing HR Onboarding Knowledge Assistant setup...")
    print()
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_text_file_ingestion,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The setup is working correctly.")
        print("\nNext steps:")
        print("1. Set your OPENAI_API_KEY environment variable")
        print("2. Run: uvicorn backend.main:app --reload")
        print("3. Test the API endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 