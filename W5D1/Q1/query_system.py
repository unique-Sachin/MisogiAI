#!/usr/bin/env python3
"""Interactive query script for the Medical AI Assistant."""

import requests
import json
import sys
from datetime import datetime

def query_system(question, user_id="interactive_user"):
    """Query the medical AI system."""
    
    base_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        health_response = requests.get(f"{base_url}/api/v1/health")
        if health_response.status_code != 200:
            print("❌ API is not running. Please start it first:")
            print("python -m uvicorn src.api.main:app --reload")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start it first:")
        print("python -m uvicorn src.api.main:app --reload")
        return None
    
    # Prepare query payload
    payload = {
        "query": question,
        "user_id": user_id
    }
    
    try:
        print(f"🔍 Querying: {question}")
        print("⏳ Processing...")
        
        # Make the query
        response = requests.post(f"{base_url}/api/v1/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*80)
            print("📋 QUERY RESULTS")
            print("="*80)
            
            print(f"❓ Question: {result['query']}")
            print(f"💰 Cost: ${result['cost']:.4f}")
            print(f"🔢 Tokens: {result['tokens_used']}")
            print(f"📚 Sources: {len(result['sources'])}")
            
            print("\n📝 ANSWER:")
            print("-" * 40)
            print(result['answer'])
            
            print("\n📖 SOURCES:")
            print("-" * 40)
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. Page {source['page']}")
                print(f"   Content: {source['content']}")
                print()
            
            return result
            
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def interactive_mode():
    """Run in interactive mode."""
    print("🏥 Medical AI Assistant - Interactive Query Mode")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for sample queries")
    print()
    
    while True:
        try:
            question = input("💬 Ask a question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if question.lower() == 'help':
                show_sample_queries()
                continue
            
            if not question:
                print("⚠️  Please enter a question.")
                continue
            
            # Query the system
            result = query_system(question)
            
            if result:
                print("\n" + "="*80)
                print("Press Enter to continue...")
                input()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_sample_queries():
    """Show sample queries for drug interactions."""
    print("\n📚 Sample Queries for Drug Interactions:")
    print("-" * 40)
    
    samples = [
        "What are the main types of drug interactions?",
        "What are pharmacokinetic interactions?",
        "How do drug-food interactions work?",
        "What are the mechanisms of drug interactions?",
        "What causes drug interactions?",
        "How can drug interactions be prevented?",
        "What are the clinical implications of drug interactions?",
        "What is the difference between pharmacokinetic and pharmacodynamic interactions?"
    ]
    
    for i, sample in enumerate(samples, 1):
        print(f"{i}. {sample}")
    
    print("\n💡 Tip: Ask specific questions about drug interactions, mechanisms, or clinical implications!")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        query_system(question)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 