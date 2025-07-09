#!/usr/bin/env python3
"""Script to manually process PDF files."""

import os
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.document_processor import MedicalDocumentProcessor

def find_pdf_files(directory: str) -> List[str]:
    """Find all PDF files in a directory."""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main():
    """Process all PDF files in the documents directory."""
    
    # Create documents directory if it doesn't exist
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)
    
    print("🔍 Looking for PDF files...")
    pdf_files = find_pdf_files(str(docs_dir))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {docs_dir}")
        print("📝 Please place your medical PDF files in the 'documents' directory")
        print("   Example: documents/medical_guide.pdf")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file}")
    
    # Initialize document processor
    print("\n🚀 Initializing document processor...")
    processor = MedicalDocumentProcessor()
    
    # Process all PDF files
    print("\n📖 Processing PDF files...")
    try:
        total_chunks = processor.process_documents(pdf_files)
        print(f"\n✅ Successfully processed {total_chunks} chunks from {len(pdf_files)} PDF files")
        print("🎉 Documents are now ready for querying!")
        
    except Exception as e:
        print(f"❌ Error processing documents: {e}")

if __name__ == "__main__":
    main() 