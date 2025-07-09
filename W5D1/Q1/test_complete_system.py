#!/usr/bin/env python3
"""Comprehensive test script for the complete Medical AI Assistant system."""

import os
import sys
import json
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all components can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from core.rag_engine import MedicalRAGEngine
        print("✅ RAG Engine import successful")
    except ImportError as e:
        print(f"❌ RAG Engine import failed: {e}")
        return False
    
    try:
        from evaluation.ragas_evaluator import MedicalRAGASEvaluator, QualityGate
        print("✅ RAGAS Evaluator import successful")
    except ImportError as e:
        print(f"❌ RAGAS Evaluator import failed: {e}")
        return False
    
    try:
        from safety.safety_system import MedicalSafetySystem
        print("✅ Safety System import successful")
    except ImportError as e:
        print(f"❌ Safety System import failed: {e}")
        return False
    
    try:
        from database.models import QueryLog, RAGASMetric, SafetyLog, Document
        print("✅ Database Models import successful")
    except ImportError as e:
        print(f"❌ Database Models import failed: {e}")
        return False
    
    try:
        from database.database import DatabaseManager
        print("✅ Database Manager import successful")
    except ImportError as e:
        print(f"❌ Database Manager import failed: {e}")
        return False
    
    return True

def test_rag_engine():
    """Test RAG engine functionality."""
    print("\n🤖 Testing RAG Engine...")
    
    try:
        from core.rag_engine import MedicalRAGEngine
        
        # Initialize without RAGAS and safety for basic test
        rag_engine = MedicalRAGEngine(enable_ragas=False, enable_safety=False)
        
        # Test basic query
        result = rag_engine.query("What is diabetes?")
        
        if result and "answer" in result:
            print("✅ RAG Engine basic query successful")
            print(f"   Answer length: {len(result['answer'])} characters")
            print(f"   Sources: {len(result.get('sources', []))}")
            return True
        else:
            print("❌ RAG Engine query failed - no answer returned")
            return False
            
    except Exception as e:
        print(f"❌ RAG Engine test failed: {e}")
        return False

def test_ragas_evaluator():
    """Test RAGAS evaluator."""
    print("\n📊 Testing RAGAS Evaluator...")
    
    try:
        from evaluation.ragas_evaluator import MedicalRAGASEvaluator, QualityGate
        
        # Test quality gate
        quality_gate = QualityGate()
        
        # Test with mock scores
        mock_scores = {
            "faithfulness": 0.95,
            "context_precision": 0.88,
            "context_recall": 0.92,
            "answer_relevancy": 0.90
        }
        
        result = quality_gate.evaluate(mock_scores)
        
        if result.get("quality_gate_passed"):
            print("✅ Quality Gate test passed")
            print(f"   Faithfulness passed: {result.get('faithfulness_passed')}")
            print(f"   Precision passed: {result.get('precision_passed')}")
            return True
        else:
            print("❌ Quality Gate test failed")
            return False
            
    except Exception as e:
        print(f"❌ RAGAS Evaluator test failed: {e}")
        return False

def test_safety_system():
    """Test safety system."""
    print("\n🔒 Testing Safety System...")
    
    try:
        from safety.safety_system import MedicalSafetySystem
        
        # Test without OpenAI for basic functionality
        safety_system = MedicalSafetySystem()
        
        # Test disclaimer
        disclaimer = safety_system.get_safety_disclaimer()
        
        if disclaimer and "MEDICAL DISCLAIMER" in disclaimer:
            print("✅ Safety System disclaimer test passed")
            print(f"   Disclaimer length: {len(disclaimer)} characters")
            return True
        else:
            print("❌ Safety System disclaimer test failed")
            return False
            
    except Exception as e:
        print(f"❌ Safety System test failed: {e}")
        return False

def test_database_setup():
    """Test database setup."""
    print("\n🗄️ Testing Database Setup...")
    
    try:
        # Set testing environment
        os.environ["TESTING"] = "true"
        
        from database.database import DatabaseManager
        from database.models import Base
        
        db_manager = DatabaseManager()
        
        # Test database creation
        db_manager.create_tables()
        print("✅ Database tables created successfully")
        
        # Test health check
        if db_manager.health_check():
            print("✅ Database health check passed")
            return True
        else:
            print("❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False

def test_integrated_system():
    """Test integrated system with all components."""
    print("\n🌐 Testing Integrated System...")
    
    try:
        from core.rag_engine import MedicalRAGEngine
        
        # Initialize with all components enabled
        rag_engine = MedicalRAGEngine(
            enable_ragas=True,
            enable_safety=True
        )
        
        # Test query
        result = rag_engine.query("What are the symptoms of diabetes?")
        
        if result and "answer" in result:
            print("✅ Integrated system query successful")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   RAGAS scores available: {'ragas_scores' in result}")
            print(f"   Safety status available: {'safety_status' in result}")
            print(f"   Quality gate passed: {result.get('quality_gate_passed', 'N/A')}")
            print(f"   Blocked: {result.get('blocked', False)}")
            return True
        else:
            print("❌ Integrated system query failed")
            return False
            
    except Exception as e:
        print(f"❌ Integrated system test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        # This would test the FastAPI endpoints
        # For now, just test that the modules can be imported
        from api.main import app
        from api.monitoring_endpoints import router
        
        print("✅ API endpoints import successful")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 Starting Comprehensive System Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("RAG Engine Test", test_rag_engine),
        ("RAGAS Evaluator Test", test_ragas_evaluator),
        ("Safety System Test", test_safety_system),
        ("Database Setup Test", test_database_setup),
        ("API Endpoints Test", test_api_endpoints),
        ("Integrated System Test", test_integrated_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 