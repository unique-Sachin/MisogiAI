import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from .embeddings import CustomSentenceTransformerEmbeddings

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class MedicalDocumentProcessor:
    """Load PDFs, split them into chunks, embed and store in ChromaDB."""

    def __init__(self, persist_directory: str = None):
        # Use environment variable or default
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./medical_vector_db")
        
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        self.embeddings = CustomSentenceTransformerEmbeddings(embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
        self.vector_store = Chroma(
            embedding_function=self.embeddings, 
            persist_directory=persist_directory
        )

    def process_documents(self, pdf_files: List[str]) -> int:
        """Ingest the list of PDF file paths into the vector store.

        Returns
        -------
        int
            Total number of chunks indexed.
        """
        documents = []
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file}")
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            split_docs = self.text_splitter.split_documents(docs)
            documents.extend(split_docs)
            print(f"  - Added {len(split_docs)} chunks")

        if documents:
            self.vector_store.add_documents(documents)
            print(f"Total chunks indexed: {len(documents)}")
        return len(documents) 