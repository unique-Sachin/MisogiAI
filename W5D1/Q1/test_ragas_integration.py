#!/usr/bin/env python3
"""Test script to verify RAGAS integration."""

import sys
import os
from pathlib import Path

# Set environment variables directly
os.environ["OPENAI_API_KEY"] = "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"
os.environ["EMBEDDING_MODEL"] = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
os.environ["LLM_MODEL"] = "gpt-4o-mini"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "./medical_vector_db"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ragas_integration():
    """Test RAGAS integration with the RAG engine."""
    print("🧪 Testing RAGAS Integration...")
    
    try:
        from core.rag_engine import MedicalRAGEngine
        
        # Initialize RAG engine with RAGAS enabled
        print("🚀 Initializing RAG engine with RAGAS...")
        rag_engine = MedicalRAGEngine(enable_ragas=True)
        
        if not rag_engine.enable_ragas:
            print("❌ RAGAS evaluation is not enabled")
            return False
        
        print("✅ RAGAS evaluation enabled successfully")
        
        # Test query with RAGAS evaluation
        print("\n🔍 Testing query with RAGAS evaluation...")
        test_query = "What are drug interactions?"
        
        result = rag_engine.query(test_query)
        
        # Check if RAGAS scores are present
        if "ragas_scores" in result:
            print("✅ RAGAS scores included in response")
            ragas_scores = result["ragas_scores"]
            
            # Check required metrics
            required_metrics = ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]
            for metric in required_metrics:
                if metric in ragas_scores:
                    print(f"   {metric}: {ragas_scores[metric]:.3f}")
                else:
                    print(f"❌ Missing metric: {metric}")
                    return False
            
            # Check quality gate
            if "quality_gate_passed" in result:
                gate_status = result["quality_gate_passed"]
                print(f"   Quality Gate: {'✅ PASSED' if gate_status else '❌ FAILED'}")
            
            # Check response time
            if "response_time_ms" in result:
                response_time = result["response_time_ms"]
                print(f"   Response Time: {response_time}ms")
                
                # Check if it meets PRD requirement (p95 < 3 seconds)
                if response_time < 3000:
                    print("   ✅ Response time meets PRD requirement")
                else:
                    print("   ⚠️ Response time exceeds PRD requirement")
            
            print("\n📊 RAGAS Integration Test Results:")
            print(f"   Faithfulness: {ragas_scores.get('faithfulness', 0):.3f} (threshold: 0.90)")
            print(f"   Context Precision: {ragas_scores.get('context_precision', 0):.3f} (threshold: 0.85)")
            print(f"   Context Recall: {ragas_scores.get('context_recall', 0):.3f}")
            print(f"   Answer Relevancy: {ragas_scores.get('answer_relevancy', 0):.3f}")
            
            return True
            
        else:
            print("❌ RAGAS scores not found in response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing RAGAS integration: {e}")
        return False

def test_quality_gate():
    """Test quality gate functionality."""
    print("\n🚪 Testing Quality Gate...")
    
    try:
        from evaluation.ragas_evaluator import QualityGate
        
        quality_gate = QualityGate()
        
        # Test passing scores
        passing_scores = {
            "faithfulness": 0.95,
            "context_precision": 0.90,
            "context_recall": 0.85,
            "answer_relevancy": 0.88
        }
        
        result = quality_gate.check(passing_scores)
        if result:
            print("✅ Quality gate correctly passes high-quality scores")
        else:
            print("❌ Quality gate incorrectly fails high-quality scores")
            return False
        
        # Test failing scores
        failing_scores = {
            "faithfulness": 0.75,  # Below threshold
            "context_precision": 0.80,  # Below threshold
            "context_recall": 0.85,
            "answer_relevancy": 0.88
        }
        
        result = quality_gate.check(failing_scores)
        if not result:
            print("✅ Quality gate correctly fails low-quality scores")
        else:
            print("❌ Quality gate incorrectly passes low-quality scores")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing quality gate: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 RAGAS Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_ragas_integration,
        test_quality_gate
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All RAGAS integration tests passed!")
        print("\n✅ Features working:")
        print("   - RAGAS evaluation integration")
        print("   - Quality gate system")
        print("   - Real-time metrics")
        print("   - Response time tracking")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 