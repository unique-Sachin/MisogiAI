#!/usr/bin/env python3
"""Test script for PDF upload functionality."""

import requests
import time
import json
from pathlib import Path

def test_pdf_upload():
    """Test PDF upload and processing."""
    print("🧪 Testing PDF Upload Functionality...")
    
    base_url = "http://localhost:8000"
    
    # First, check if API is running
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code != 200:
            print("❌ API is not running. Please start it first:")
            print("cd Q1 && python -m uvicorn src.api.main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start it first:")
        print("cd Q1 && python -m uvicorn src.api.main:app --reload")
        return
    
    # Test 1: List existing documents
    print("\n1. Testing document list...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_count']} existing documents")
            for doc in data['documents']:
                print(f"   - {doc['filename']}: {doc['status']} ({doc['chunks_processed']} chunks)")
        else:
            print(f"❌ Failed to list documents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
    
    # Test 2: Upload a PDF (you need to provide a sample PDF)
    print("\n2. Testing PDF upload...")
    
    # Look for sample PDFs in common locations
    sample_paths = [
        "sample.pdf",
        "documents/sample.pdf",
        "test.pdf",
        "medical_sample.pdf"
    ]
    
    sample_pdf = None
    for path in sample_paths:
        if Path(path).exists():
            sample_pdf = path
            break
    
    if not sample_pdf:
        print("⚠️  No sample PDF found. Please create a sample PDF file.")
        print("   You can:")
        print("   1. Create a file called 'sample.pdf' in the current directory")
        print("   2. Or place any PDF in the 'documents/' directory")
        print("   3. Then run this test again")
        
        # Create a simple example
        print("\n📝 Example usage:")
        print("   curl -X POST 'http://localhost:8000/api/v1/documents/upload' \\")
        print("        -H 'Content-Type: multipart/form-data' \\")
        print("        -F 'file=@your_medical_document.pdf'")
        return
    
    try:
        print(f"📤 Uploading {sample_pdf}...")
        
        with open(sample_pdf, 'rb') as f:
            files = {'file': (Path(sample_pdf).name, f, 'application/pdf')}
            response = requests.post(f"{base_url}/api/v1/documents/upload", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            document_id = upload_result['document_id']
            print(f"✅ Upload successful!")
            print(f"   Document ID: {document_id}")
            print(f"   Filename: {upload_result['filename']}")
            print(f"   Status: {upload_result['status']}")
            
            # Test 3: Monitor processing status
            print("\n3. Monitoring processing status...")
            max_wait = 60  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(f"{base_url}/api/v1/documents/status/{document_id}")
                    if response.status_code == 200:
                        status = response.json()
                        print(f"   Status: {status['status']} ({status['chunks_processed']} chunks)")
                        
                        if status['status'] == 'completed':
                            print(f"✅ Processing completed! {status['chunks_processed']} chunks processed")
                            break
                        elif status['status'] == 'failed':
                            print(f"❌ Processing failed: {status['error_message']}")
                            break
                    else:
                        print(f"❌ Failed to get status: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"❌ Error checking status: {e}")
                    break
                
                time.sleep(2)
            
            # Test 4: Query the uploaded document
            print("\n4. Testing query with uploaded document...")
            try:
                query_payload = {
                    "query": "What is this document about?",
                    "user_id": "test_user"
                }
                
                response = requests.post(f"{base_url}/api/v1/query", json=query_payload)
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Query successful!")
                    print(f"   Answer length: {len(result['answer'])} characters")
                    print(f"   Sources found: {len(result['sources'])}")
                    print(f"   Answer preview: {result['answer'][:200]}...")
                else:
                    print(f"❌ Query failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")

def show_usage():
    """Show usage examples."""
    print("\n📚 PDF Upload Usage Examples:")
    print("\n1. Using curl:")
    print("   curl -X POST 'http://localhost:8000/api/v1/documents/upload' \\")
    print("        -H 'Content-Type: multipart/form-data' \\")
    print("        -F 'file=@medical_document.pdf'")
    
    print("\n2. Using Python requests:")
    print("   import requests")
    print("   with open('medical_document.pdf', 'rb') as f:")
    print("       files = {'file': ('medical_document.pdf', f, 'application/pdf')}")
    print("       response = requests.post('http://localhost:8000/api/v1/documents/upload', files=files)")
    
    print("\n3. Using the FastAPI docs:")
    print("   Go to http://localhost:8000/docs")
    print("   Find the POST /api/v1/documents/upload endpoint")
    print("   Click 'Try it out' and upload your PDF file")

if __name__ == "__main__":
    test_pdf_upload()
    show_usage() 