#!/usr/bin/env python3
"""
Demo script showing how to use the enhanced RAG system with source references.
Run this after building the index with sample knowledge base files.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.retriever import retrieve_with_references, retrieve
from app.intent_classifier import classify_intent

def demo_references():
    """Demonstrate the reference feature with sample queries."""
    
    print("🔍 RAG System with Source References Demo")
    print("=" * 50)
    
    # Sample queries for different intents
    queries = [
        "How do I reset my password?",
        "Why was I charged twice?", 
        "Can you add dark mode?"
    ]
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 30)
        
        # Classify intent
        intent = classify_intent(query)
        print(f"🎯 Detected intent: {intent}")
        
        # Retrieve with references
        results = retrieve_with_references(query, intent, k=3)
        
        if results:
            print(f"📚 Retrieved {len(results)} relevant chunks:")
            for i, result in enumerate(results, 1):
                print(f"\n  Chunk {i}:")
                print(f"    📄 Source: {result['metadata'].get('source_file', 'unknown')}")
                print(f"    🧩 Chunk #{result['metadata'].get('chunk_index', 0)}")
                print(f"    📊 Similarity: {1 - result['distance']:.3f}")
                print(f"    💬 Content: {result['content'][:100]}...")
        else:
            print("  ❌ No relevant chunks found")
            
        print("\n" + "="*50)

def compare_legacy_vs_enhanced():
    """Compare legacy retrieve vs enhanced retrieve_with_references."""
    
    print("\n🔄 Comparing Legacy vs Enhanced Retrieval")
    print("=" * 50)
    
    query = "password reset"
    intent = "technical"
    
    # Legacy method
    print("\n📜 Legacy retrieve():")
    legacy_results = retrieve(query, intent, k=2)
    for i, doc in enumerate(legacy_results, 1):
        print(f"  {i}. {doc[:80]}...")
    
    # Enhanced method
    print("\n✨ Enhanced retrieve_with_references():")
    enhanced_results = retrieve_with_references(query, intent, k=2)
    for i, result in enumerate(enhanced_results, 1):
        print(f"  {i}. {result['content'][:80]}...")
        print(f"     Source: {result['metadata'].get('source_file', 'N/A')}")
        print(f"     Similarity: {1 - result['distance']:.3f}")

if __name__ == "__main__":
    try:
        demo_references()
        compare_legacy_vs_enhanced()
        print("\n✅ Demo completed successfully!")
        print("\n💡 To see this in action:")
        print("   1. Build the index: python -c 'from app.retriever import build_index; build_index()'")
        print("   2. Run Streamlit UI: streamlit run ui/streamlit_app.py")
        print("   3. Toggle 'Show source references' to see the difference")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure to build the index first:")
        print("   python -c 'from app.retriever import build_index; build_index()'") 