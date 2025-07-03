from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from typing import List

from document_analyzer import tools  # type: ignore
from document_analyzer.tools import (
    AddDocumentIn, AddDocumentOut,
    AnalyzeDocumentIn, AnalyzeDocumentOut,
    SentimentIn, SentimentOut,
    KeywordsIn, KeywordsOut,
    SearchIn, SearchHit,
)

app = FastAPI(title="Document Analyzer MCP-Compatible Tool Server")

# Error handler
@app.exception_handler(ValueError)
async def value_error_handler(_, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": {"code": "VALUE_ERROR", "message": str(exc)}})


@app.post("/add_document", response_model=AddDocumentOut)
async def add_document(payload: AddDocumentIn):
    try:
        return tools.add_document(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_document", response_model=AnalyzeDocumentOut)
async def analyze_document(payload: AnalyzeDocumentIn):
    try:
        return tools.analyze_document(payload)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_sentiment", response_model=SentimentOut)
async def get_sentiment(payload: SentimentIn):
    return tools.get_sentiment(payload)


@app.post("/extract_keywords", response_model=KeywordsOut)
async def extract_keywords(payload: KeywordsIn):
    return tools.extract_keywords(payload)


@app.post("/search_documents", response_model=List[SearchHit])
async def search_documents(payload: SearchIn):
    return tools.search_documents(payload) 