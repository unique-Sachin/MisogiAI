#!/usr/bin/env python3
"""
Test Query Validator - Validates the test set queries and runs them through the RAG system
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.intent_classifier import classify_intent
from app.retriever import retrieve_with_references

def load_test_queries(file_path: str) -> Dict[str, List[str]]:
    """Load test queries from the text file."""
    queries = {"technical": [], "billing": [], "feature_request": []}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and ':' in line:
                intent, query = line.split(':', 1)
                intent = intent.strip()
                query = query.strip()
                if intent in queries:
                    queries[intent].append(query)
    
    return queries

def validate_query_distribution(queries: Dict[str, List[str]]) -> None:
    """Validate that we have the expected number of queries per intent."""
    print("📊 Query Distribution Validation")
    print("=" * 40)
    
    total_queries = 0
    for intent, query_list in queries.items():
        count = len(query_list)
        total_queries += count
        status = "✅" if count == 20 else "❌"
        print(f"{status} {intent}: {count} queries")
    
    print(f"\n📈 Total queries: {total_queries}")
    expected_total = 60
    if total_queries == expected_total:
        print("✅ Query count validation passed!")
    else:
        print(f"❌ Expected {expected_total} queries, got {total_queries}")

def test_intent_classification(queries: Dict[str, List[str]], sample_size: int = 5) -> Dict[str, Dict[str, int]]:
    """Test intent classification accuracy on a sample of queries."""
    print(f"\n🎯 Intent Classification Test (sample size: {sample_size})")
    print("=" * 50)
    
    results = {}
    
    for expected_intent, query_list in queries.items():
        print(f"\nTesting {expected_intent} queries:")
        results[expected_intent] = {"correct": 0, "incorrect": 0, "total": 0}
        
        # Test first N queries from each intent
        sample_queries = query_list[:sample_size]
        
        for i, query in enumerate(sample_queries, 1):
            try:
                predicted_intent = classify_intent(query)
                is_correct = predicted_intent == expected_intent
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} Query {i}: '{query[:50]}...'")
                print(f"      Expected: {expected_intent}, Got: {predicted_intent}")
                
                results[expected_intent]["total"] += 1
                if is_correct:
                    results[expected_intent]["correct"] += 1
                else:
                    results[expected_intent]["incorrect"] += 1
                    
            except Exception as e:
                print(f"  ❌ Query {i}: Error - {e}")
                results[expected_intent]["total"] += 1
                results[expected_intent]["incorrect"] += 1
    
    return results

def test_retrieval_system(queries: Dict[str, List[str]], sample_size: int = 3) -> None:
    """Test the retrieval system with sample queries."""
    print(f"\n🔍 Retrieval System Test (sample size: {sample_size})")
    print("=" * 50)
    
    for intent, query_list in queries.items():
        print(f"\nTesting {intent} retrieval:")
        
        # Test first N queries from each intent
        sample_queries = query_list[:sample_size]
        
        for i, query in enumerate(sample_queries, 1):
            try:
                results = retrieve_with_references(query, intent=intent, k=3)
                print(f"  📝 Query {i}: '{query[:50]}...'")
                print(f"      Retrieved {len(results)} documents")
                
                # Show first result if available
                if results:
                    first_result = results[0]
                    content_preview = first_result['content'][:100] + "..." if len(first_result['content']) > 100 else first_result['content']
                    print(f"      Top result: {content_preview}")
                    if 'metadata' in first_result:
                        print(f"      Source: {first_result['metadata'].get('source_file', 'Unknown')}")
                else:
                    print("      ⚠️  No documents retrieved")
                    
            except Exception as e:
                print(f"  ❌ Query {i}: Retrieval error - {e}")

def generate_classification_report(results: Dict[str, Dict[str, int]]) -> None:
    """Generate a classification accuracy report."""
    print(f"\n📋 Classification Accuracy Report")
    print("=" * 40)
    
    overall_correct = 0
    overall_total = 0
    
    for intent, stats in results.items():
        correct = stats["correct"]
        total = stats["total"]
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print(f"{intent}:")
        print(f"  Correct: {correct}/{total} ({accuracy:.1f}%)")
        
        overall_correct += correct
        overall_total += total
    
    overall_accuracy = (overall_correct / overall_total * 100) if overall_total > 0 else 0
    print(f"\nOverall Accuracy: {overall_correct}/{overall_total} ({overall_accuracy:.1f}%)")

def main():
    """Main function to run all tests."""
    print("🧪 RAG System Test Query Validator")
    print("=" * 50)
    
    # Load test queries
    try:
        queries = load_test_queries("test_queries.txt")
    except FileNotFoundError:
        print("❌ Error: test_queries.txt not found!")
        return
    
    # Validate query distribution
    validate_query_distribution(queries)
    
    # Test intent classification
    classification_results = test_intent_classification(queries, sample_size=5)
    generate_classification_report(classification_results)
    
    # Test retrieval system
    test_retrieval_system(queries, sample_size=3)
    
    print("\n🎉 Test validation complete!")
    print("\nNext steps:")
    print("1. Build the knowledge base index: python -m app.retriever")
    print("2. Run the full test suite: python test_query_validator.py")
    print("3. Start the Streamlit app: streamlit run ui/streamlit_app.py")

if __name__ == "__main__":
    main() 