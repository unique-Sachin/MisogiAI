from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from functools import lru_cache
import os

from dotenv import load_dotenv

# LangChain imports (using new split packages)
from langchain_community.vectorstores import Pinecone as PineconeVectorStore  # type: ignore
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # type: ignore

# Pinecone v3 client
from pinecone import Pinecone, ServerlessSpec  # type: ignore

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV") or "us-east-1"
INDEX_NAME = os.getenv("INDEX_NAME") or "mcp-chatbot-index"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="MCP Expert Chatbot API")

# Enable CORS for local dev and public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] | None = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@lru_cache(maxsize=1)
def get_chain() -> RetrievalQA:
    """Create and cache the RetrievalQA chain."""
    # Pinecone client + index
    pc = Pinecone(api_key=PINECONE_API_KEY or "")  # type: ignore[arg-type]
    index = pc.Index(INDEX_NAME)

    # Embeddings and vector store
    embeddings = OpenAIEmbeddings()  # type: ignore[call-arg]
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")
    retriever = vectorstore.as_retriever()

    # Chat model
    llm = ChatOpenAI(temperature=0.2, model="gpt-4o-mini")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_chain

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    chain = get_chain()
    response = chain.invoke({"query": req.message})  # type: ignore
    answer = response["result"]
    sources = [doc.metadata.get("source") for doc in response.get("source_documents", [])]

    return ChatResponse(answer=answer, sources=sources) 