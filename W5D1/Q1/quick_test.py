#!/usr/bin/env python3
"""Quick test script to verify the Medical AI Assistant system."""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def quick_test():
    """Run quick tests to verify system functionality."""
    print("🚀 Quick System Test")
    print("=" * 40)
    
    # Test 1: Basic imports
    print("\n1. Testing imports...")
    try:
        from core.rag_engine import MedicalRAGEngine
        from evaluation.ragas_evaluator import QualityGate
        from safety.safety_system import MedicalSafetySystem
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Basic RAG engine
    print("\n2. Testing RAG engine...")
    try:
        rag_engine = MedicalRAGEngine(enable_ragas=False, enable_safety=False)
        result = rag_engine.query("What is diabetes?")
        if result and 'answer' in result:
            print("✅ RAG engine working")
            print(f"   Answer length: {len(result['answer'])} chars")
        else:
            print("❌ RAG engine failed")
            return False
    except Exception as e:
        print(f"❌ RAG engine error: {e}")
        return False
    
    # Test 3: Quality gate
    print("\n3. Testing quality gate...")
    try:
        quality_gate = QualityGate()
        test_scores = {
            "faithfulness": 0.95,
            "context_precision": 0.88,
            "context_recall": 0.92,
            "answer_relevancy": 0.90
        }
        result = quality_gate.evaluate(test_scores)
        if result.get("quality_gate_passed"):
            print("✅ Quality gate working")
        else:
            print("❌ Quality gate failed")
            return False
    except Exception as e:
        print(f"❌ Quality gate error: {e}")
        return False
    
    # Test 4: Safety system
    print("\n4. Testing safety system...")
    try:
        safety_system = MedicalSafetySystem()
        disclaimer = safety_system.get_safety_disclaimer()
        if disclaimer and "MEDICAL DISCLAIMER" in disclaimer:
            print("✅ Safety system working")
        else:
            print("❌ Safety system failed")
            return False
    except Exception as e:
        print(f"❌ Safety system error: {e}")
        return False
    
    # Test 5: Database (SQLite for testing)
    print("\n5. Testing database...")
    try:
        os.environ["TESTING"] = "true"
        from database.database import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.create_tables()
        if db_manager.health_check():
            print("✅ Database working")
        else:
            print("❌ Database failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print("\n🎉 All quick tests passed!")
    print("\nNext steps:")
    print("1. Set your OpenAI API key in .env file")
    print("2. Run: python -m uvicorn src.api.main:app --reload")
    print("3. Test API at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1) 