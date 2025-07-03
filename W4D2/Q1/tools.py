from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from . import storage, analyzer, search

# ----------------------------
# Pydantic Models (IO Schemas)
# ----------------------------

class Metadata(BaseModel):
    category: Optional[str] = None
    language: Optional[str] = None

class DocumentData(BaseModel):
    title: str
    author: str
    date: str
    content: str
    metadata: Metadata = Field(default_factory=Metadata)

class AddDocumentIn(BaseModel):
    document_data: DocumentData

class AddDocumentOut(BaseModel):
    document_id: int

class AnalyzeDocumentIn(BaseModel):
    document_id: int

class AnalyzeDocumentOut(BaseModel):
    sentiment: str
    keywords: List[str]
    readability: float
    stats: Dict[str, Any]

class SentimentIn(BaseModel):
    text: str

class SentimentOut(BaseModel):
    sentiment: str

class KeywordsIn(BaseModel):
    text: str
    limit: int = 5

class KeywordsOut(BaseModel):
    keywords: List[str]

class SearchIn(BaseModel):
    query: str

class SearchHit(BaseModel):
    id: int
    title: str
    matched_snippet: str

# ----------------------------
# Tool Logic
# ----------------------------

def add_document(in_data: AddDocumentIn) -> AddDocumentOut:
    doc_dict = in_data.document_data.dict()
    new_id = storage.add_document(doc_dict)
    return AddDocumentOut(document_id=new_id)

def analyze_document(in_data: AnalyzeDocumentIn) -> AnalyzeDocumentOut:
    doc = storage.get_document(in_data.document_id)
    if not doc:
        raise ValueError("Document not found")
    analysis = analyzer.analyze_document_content(doc["content"])
    return AnalyzeDocumentOut(**analysis)

def get_sentiment(in_data: SentimentIn) -> SentimentOut:
    sentiment = analyzer.get_sentiment(in_data.text)
    return SentimentOut(sentiment=sentiment)

def extract_keywords(in_data: KeywordsIn) -> KeywordsOut:
    keywords = analyzer.extract_keywords(in_data.text, limit=in_data.limit or 5)
    return KeywordsOut(keywords=keywords)

def search_documents(in_data: SearchIn) -> List[SearchHit]:
    results = search.search_documents(in_data.query)
    return [SearchHit(**r) for r in results] 