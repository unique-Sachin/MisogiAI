# Medical AI Assistant - Product Requirements Document (PRD)

## 1. Project Overview

### 1.1 Product Vision
Build a production-ready Medical Knowledge Assistant RAG pipeline for healthcare professionals to query medical literature, drug interactions, and clinical guidelines with comprehensive RAGAS evaluation framework ensuring accuracy and safety.

### 1.2 Success Criteria
- **Faithfulness Score**: >0.90 (medical accuracy)
- **Context Precision**: >0.85
- **Response Latency**: p95 < 3 seconds
- **Zero harmful medical advice**: Safety-first approach
- **Working RAGAS monitoring**: Real-time evaluation system

### 1.3 Target Users
- Healthcare professionals
- Medical researchers
- Clinical decision support systems
- Medical information specialists

## 2. Technical Architecture

### 2.1 Core Technology Stack

```yaml
# AI/ML Components
Embedding Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
LLM: OpenAI GPT-4o-mini
RAG Framework: LangChain (langchain==0.1.0)
Evaluation: RAGAS framework (ragas==0.1.0)

# Backend Services
Framework: FastAPI (Python 3.11+)
Vector Database: ChromaDB (via LangChain)
Document Database: PostgreSQL
Cache: Redis
Message Queue: Celery + Redis

# Infrastructure
Containerization: Docker + Docker Compose
Monitoring: Prometheus + Grafana
Logging: ELK Stack (Elasticsearch, Logstash, Kibana)
```

### 2.2 Model Specifications

```python
# Embedding Model Details
Model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
Dimensions: 384
Languages: 50+ languages support
Max Sequence Length: 512 tokens
Size: ~118MB (lightweight, fast inference)

# LLM Details
Model: "gpt-4o-mini"
Context Window: 128k tokens
Cost: ~10x cheaper than GPT-4
Speed: ~2x faster than GPT-4
Quality: 95% of GPT-4 quality for RAG tasks
```

## 3. System Components

### 3.1 Document Ingestion Pipeline

**Requirements:**
- Support PDF processing (LangChain DocumentLoaders)
- Semantic chunking with LangChain TextSplitters
- Local embedding generation with custom embeddings
- Metadata extraction and storage
- Multilingual document support

**Implementation:**
```python
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
import numpy as np

class CustomSentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
        
    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()

class MedicalDocumentProcessor:
    def __init__(self):
        self.embeddings = CustomSentenceTransformerEmbeddings(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./medical_vector_db"
        )
        
    def process_documents(self, pdf_files: List[str]):
        documents = []
        for pdf_file in pdf_files:
            # Load PDF with LangChain
            loader = PyMuPDFLoader(pdf_file)
            docs = loader.load()
            
            # Split documents
            split_docs = self.text_splitter.split_documents(docs)
            documents.extend(split_docs)
            
        # Add to vector store
        self.vector_store.add_documents(documents)
        return len(documents)
```

### 3.2 RAG Query Engine

**Requirements:**
- Query preprocessing and expansion
- Vector similarity search with LangChain
- Context ranking and filtering
- Response generation with LangChain ChatOpenAI
- Source attribution and retrieval chain

**Implementation:**
```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.schema import Document

class MedicalRAGEngine:
    def __init__(self):
        self.embeddings = CustomSentenceTransformerEmbeddings(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./medical_vector_db"
        )
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1000
        )
        
        # Create retrieval chain
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Define medical prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a medical knowledge assistant. 
            Provide accurate, evidence-based information using only the provided context.
            Always cite sources and indicate when information is outside your knowledge.
            Never provide direct medical advice or diagnosis.
            
            Context: {context}
            
            Question: {question}
            
            Please provide a comprehensive answer based on the context provided:"""
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
        
    def query(self, user_query: str, top_k: int = 5) -> dict:
        """Process medical query through LangChain RAG pipeline"""
        
        with get_openai_callback() as cb:
            # Execute the chain
            result = self.qa_chain({"query": user_query})
            
            # Extract information
            answer = result["result"]
            source_documents = result["source_documents"]
            
            # Format sources
            sources = []
            for doc in source_documents:
                sources.append({
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown"),
                    "content": doc.page_content[:200] + "..."
                })
            
            return {
                "query": user_query,
                "answer": answer,
                "sources": sources,
                "context": [doc.page_content for doc in source_documents],
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost
            }
```

### 3.3 RAGAS Evaluation System

**Requirements:**
- Real-time evaluation of all responses
- Four core metrics implementation
- Quality gate with thresholds
- Batch evaluation capabilities
- Monitoring dashboard integration

**Core Metrics:**
```python
from ragas.metrics import (
    context_precision,    # >0.85 threshold
    context_recall,       # Quality indicator
    faithfulness,         # >0.90 threshold (critical)
    answer_relevancy      # User satisfaction
)
from ragas import evaluate
from langchain.schema import Document
import pandas as pd

class MedicalRAGASEvaluator:
    def __init__(self):
        self.metrics = [context_precision, context_recall, 
                       faithfulness, answer_relevancy]
        
        # Configure RAGAS to use GPT-4o-mini
        self._configure_ragas_models()
        
    def _configure_ragas_models(self):
        """Configure RAGAS to use our LangChain models"""
        from ragas.llms import LangchainLLM
        
        # Use our LangChain ChatOpenAI instance
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        langchain_llm = LangchainLLM(llm=llm)
        
        # Configure metrics to use our LLM
        for metric in self.metrics:
            if hasattr(metric, 'llm'):
                metric.llm = langchain_llm
                
    def evaluate_response(self, query: str, context: List[str], 
                         response: str, ground_truth: str = None) -> dict:
        """Evaluate RAG response using RAGAS metrics with LangChain integration"""
        
        # Prepare evaluation dataset in RAGAS format
        eval_dataset = {
            "question": [query],
            "answer": [response],
            "contexts": [context],
            "ground_truth": [ground_truth] if ground_truth else [""]
        }
        
        # Convert to DataFrame for RAGAS
        eval_df = pd.DataFrame(eval_dataset)
        
        # Run RAGAS evaluation
        result = evaluate(
            dataset=eval_df,
            metrics=self.metrics
        )
        
        scores = {
            "context_precision": result["context_precision"],
            "context_recall": result["context_recall"],
            "faithfulness": result["faithfulness"],
            "answer_relevancy": result["answer_relevancy"]
        }
        
        # Apply quality gates
        quality_gate_passed = (
            scores["faithfulness"] >= 0.90 and
            scores["context_precision"] >= 0.85
        )
        
        return {
            **scores,
            "quality_gate_passed": quality_gate_passed,
            "evaluation_timestamp": pd.Timestamp.now()
        }
        
    def batch_evaluate(self, queries: List[str], contexts: List[List[str]], 
                      responses: List[str]) -> pd.DataFrame:
        """Batch evaluation for multiple queries"""
        
        eval_dataset = {
            "question": queries,
            "answer": responses,
            "contexts": contexts,
            "ground_truth": [""] * len(queries)
        }
        
        eval_df = pd.DataFrame(eval_dataset)
        result = evaluate(dataset=eval_df, metrics=self.metrics)
        
        return result
```

## 4. API Specifications

### 4.1 Core Endpoints

**Medical Query API:**
```python
POST /api/v1/query
Content-Type: application/json

Request:
{
    "query": "What are the drug interactions with warfarin?",
    "user_id": "healthcare_provider_123",
    "context": "emergency_department",
    "language": "en"  # Optional, auto-detected
}

Response:
{
    "answer": "Warfarin interacts with multiple medications...",
    "sources": [
        {
            "source": "clinical_guideline_v1.pdf",
            "page": 42,
            "relevance_score": 0.94
        }
    ],
    "ragas_scores": {
        "faithfulness": 0.95,
        "context_precision": 0.87,
        "context_recall": 0.91,
        "answer_relevancy": 0.92
    },
    "confidence": "high",
    "response_time_ms": 847,
    "language": "en",
    "passed_quality_gate": true
}
```

**Document Management API:**
```python
POST /api/v1/documents/upload
GET /api/v1/documents/status/{document_id}
DELETE /api/v1/documents/{document_id}
GET /api/v1/documents/list
```

**Monitoring API:**
```python
GET /api/v1/metrics/dashboard
GET /api/v1/metrics/realtime
POST /api/v1/evaluation/batch
GET /api/v1/health
```

### 4.2 Authentication & Authorization

**Requirements:**
- JWT-based authentication
- Role-based access control
- Rate limiting per user/organization
- Audit logging

## 5. Data Architecture

### 5.1 Vector Database Schema (ChromaDB)

```python
# Document Chunks
{
    "id": "doc_chunk_uuid",
    "content": "medical_text_chunk",
    "embedding": [0.1, 0.2, ...],  # 384-dimensional vector
    "metadata": {
        "source": "clinical_guideline_v1.pdf",
        "chunk_index": 42,
        "medical_specialty": "cardiology",
        "document_type": "guideline",
        "language": "en",
        "last_updated": "2024-01-15",
        "confidence_score": 0.95
    }
}
```

### 5.2 PostgreSQL Schema

```sql
-- RAGAS Metrics Table
CREATE TABLE ragas_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_precision FLOAT NOT NULL,
    context_recall FLOAT NOT NULL,
    faithfulness FLOAT NOT NULL,
    answer_relevancy FLOAT NOT NULL,
    response_time_ms INTEGER NOT NULL,
    passed_quality_gate BOOLEAN NOT NULL,
    user_id VARCHAR(100),
    INDEX idx_timestamp (timestamp),
    INDEX idx_quality_gate (passed_quality_gate)
);

-- Query Logs Table
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    retrieved_contexts JSONB,
    user_id VARCHAR(100),
    language VARCHAR(10),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_language (language)
);

-- Document Metadata Table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    document_type VARCHAR(50),
    medical_specialty VARCHAR(100),
    language VARCHAR(10),
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'pending',
    chunk_count INTEGER DEFAULT 0
);
```

## 6. Safety & Quality System

### 6.1 Multi-Layer Safety Architecture

**Safety Layers:**
1. **Query Classification**: Detect harmful/inappropriate queries
2. **Context Filtering**: Ensure retrieved content is appropriate
3. **RAGAS Evaluation**: Real-time quality assessment
4. **Response Filtering**: Final safety check before delivery
5. **Audit Trail**: Complete logging for accountability

**Implementation:**
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict

class QueryClassification(BaseModel):
    is_medical_query: bool = Field(description="Whether this is a medical query")
    is_harmful: bool = Field(description="Whether this query could be harmful")
    query_type: str = Field(description="Type of query: information, diagnosis, treatment, etc.")
    risk_level: str = Field(description="Risk level: low, medium, high")

class MedicalSafetySystem:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        self.harm_classifier = self._create_harm_classifier()
        self.quality_gate = QualityGate(
            min_faithfulness=0.90,
            min_context_precision=0.85
        )
        
    def _create_harm_classifier(self):
        """Create LangChain-based harm classifier"""
        
        parser = PydanticOutputParser(pydantic_object=QueryClassification)
        
        prompt = PromptTemplate(
            template="""You are a medical safety classifier. Analyze the following query:
            
            Query: {query}
            
            Classify this query based on:
            1. Is it a legitimate medical information request?
            2. Could it be harmful if answered directly?
            3. What type of medical query is this?
            4. What's the risk level?
            
            {format_instructions}
            """,
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return LLMChain(llm=self.llm, prompt=prompt, output_parser=parser)
        
    def validate_query(self, query: str) -> Dict:
        """Validate query using LangChain safety classifier"""
        
        try:
            classification = self.harm_classifier.run(query=query)
            
            # Determine if query should be blocked
            should_block = (
                classification.is_harmful or
                classification.query_type in ["diagnosis", "treatment"] or
                classification.risk_level == "high"
            )
            
            return {
                "is_safe": not should_block,
                "classification": classification.dict(),
                "block_reason": "Harmful or inappropriate medical query" if should_block else None
            }
            
        except Exception as e:
            # Default to blocking on error
            return {
                "is_safe": False,
                "classification": None,
                "block_reason": f"Classification error: {str(e)}"
            }
        
    def validate_response(self, response: str, ragas_scores: dict) -> Dict:
        """Validate response using RAGAS thresholds and content analysis"""
        
        # Check RAGAS thresholds
        faithfulness_passed = ragas_scores.get("faithfulness", 0) >= 0.90
        precision_passed = ragas_scores.get("context_precision", 0) >= 0.85
        
        # Content safety check using LangChain
        content_safety = self._check_response_content(response)
        
        quality_gate_passed = (
            faithfulness_passed and 
            precision_passed and 
            content_safety["is_safe"]
        )
        
        return {
            "quality_gate_passed": quality_gate_passed,
            "faithfulness_passed": faithfulness_passed,
            "precision_passed": precision_passed,
            "content_safety": content_safety,
            "ragas_scores": ragas_scores
        }
        
    def _check_response_content(self, response: str) -> Dict:
        """Check response content for safety using LangChain"""
        
        safety_prompt = PromptTemplate(
            template="""Analyze this medical response for safety concerns:
            
            Response: {response}
            
            Check for:
            1. Direct medical advice or diagnosis
            2. Treatment recommendations
            3. Harmful or dangerous information
            4. Inappropriate medical claims
            
            Respond with 'SAFE' if appropriate, 'UNSAFE' if concerning, followed by brief explanation.
            """,
            input_variables=["response"]
        )
        
        safety_chain = LLMChain(llm=self.llm, prompt=safety_prompt)
        
        try:
            safety_result = safety_chain.run(response=response)
            is_safe = safety_result.strip().startswith("SAFE")
            
            return {
                "is_safe": is_safe,
                "safety_analysis": safety_result,
                "check_timestamp": pd.Timestamp.now()
            }
            
        except Exception as e:
            # Default to unsafe on error
            return {
                "is_safe": False,
                "safety_analysis": f"Safety check failed: {str(e)}",
                "check_timestamp": pd.Timestamp.now()
            }

class QualityGate:
    def __init__(self, min_faithfulness: float, min_context_precision: float):
        self.min_faithfulness = min_faithfulness
        self.min_context_precision = min_context_precision
        
    def check(self, ragas_scores: dict) -> bool:
        """Check if response passes quality gates"""
        return (
            ragas_scores.get("faithfulness", 0) >= self.min_faithfulness and
            ragas_scores.get("context_precision", 0) >= self.min_context_precision
        )
```

### 6.2 Quality Gates

**Automatic Quality Gates:**
- Faithfulness < 0.90: Block response
- Context Precision < 0.85: Block response
- Contains diagnostic advice: Block response
- Contains treatment recommendations: Block response

## 7. Monitoring & Observability

### 7.1 Real-time Metrics Dashboard

**Key Metrics:**
```python
# System Performance
- Response latency (p50, p95, p99)
- Query throughput (queries/sec)
- Error rates by endpoint
- Resource utilization

# RAGAS Metrics
- Average faithfulness score
- Context precision trends
- Quality gate pass rate
- Metric distribution histograms

# Business Metrics
- User activity patterns
- Query categories
- Document usage statistics
- Language distribution
```

### 7.2 Alerting System

**Critical Alerts:**
- Faithfulness score drops below 0.90
- Quality gate failure rate > 5%
- Response latency > 3 seconds
- System error rate > 1%~

## 8. Development Guidelines

### 8.1 Code Structure

```
├── src/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   │   ├── rag_engine.py      # RAG implementation
│   │   ├── embeddings.py      # Embedding management
│   │   └── safety.py          # Safety systems
│   ├── evaluation/             # RAGAS evaluation
│   ├── database/    ~          # Database models
│   ├── monitoring/            # Metrics and logging
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
├── docs/                      # Documentation
├── docker/                    # Container configs
└── scripts/                   # Deployment scripts
```

### 8.2 Development Standards

**Code Quality:**
- Type hints for all functions
- Comprehensive docstrings
- Unit test coverage >90%
- Integration tests for all endpoints
- Performance benchmarks

**Error Handling:**
```python
class MedicalRAGException(Exception):
    """Base exception for medical RAG system"""
    pass

class EmbeddingError(MedicalRAGException):
    """Embedding generation failed"""
    pass

class RAGASEvaluationError(MedicalRAGException):
    """RAGAS evaluation failed"""
    pass
```

## 9. Deployment Requirements

### 9.1 Docker Configuration

**Services:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - chromadb
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=medical_ai
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      
  redis:
    image: redis:7-alpine
    
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
      
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 9.2 Environment Variables

```bash
# API Configuration
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
LLM_MODEL=gpt-4o-mini

# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/medical_ai
REDIS_URL=redis://redis:6379/0
CHROMADB_URL=http://chromadb:8000

# RAGAS Configuration
RAGAS_FAITHFULNESS_THRESHOLD=0.90
RAGAS_CONTEXT_PRECISION_THRESHOLD=0.85

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
```

## 10. Testing Strategy

### 10.1 Test Categories

**Unit Tests:**
```python
# Test embedding generation
def test_embedding_generation():
    embedder = MedicalEmbeddingPipeline()
    text = "Warfarin is an anticoagulant medication"
    embedding = embedder.embed_query(text)
    assert embedding.shape == (384,)
    assert np.linalg.norm(embedding) == pytest.approx(1.0, rel=1e-5)

# Test RAGAS evaluation
def test_ragas_evaluation():
    evaluator = MedicalRAGASEvaluator()
    scores = evaluator.evaluate_response(
        query="What is warfarin?",
        context=["Warfarin is an anticoagulant..."],
        response="Warfarin is a blood thinner..."
    )
    assert scores['faithfulness'] > 0.8
```

**Integration Tests:**
```python
# Test complete RAG pipeline
def test_end_to_end_query():
    client = TestClient(app)
    response = client.post("/api/v1/query", json={
        "query": "What are warfarin drug interactions?",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    assert response.json()['ragas_scores']['faithfulness'] > 0.90
```

### 10.2 Performance Tests

**Load Testing:**
- 100 concurrent users
- 1000 queries/minute sustained
- Response time < 3 seconds p95
- Zero errors under normal load

## 11. Deliverables Checklist

### 11.1 Core System
- [ ] Medical document ingestion pipeline
- [ ] Sentence transformer embedding integration
- [ ] ChromaDB vector storage
- [ ] RAG query engine with GPT-4o-mini
- [ ] RESTful API with all endpoints

### 11.2 RAGAS Evaluation
- [ ] Real-time RAGAS evaluation
- [ ] All four core metrics implemented
- [ ] Quality gate system
- [ ] Batch evaluation capabilities
- [ ] Metrics storage and retrieval

### 11.3 Safety & Monitoring
- [ ] Multi-layer safety system
- [ ] Real-time monitoring dashboard
- [ ] Alerting system
- [ ] Audit logging
- [ ] Performance monitoring

### 11.4 Production Readiness
- [ ] Docker containerization
- [ ] Environment configuration
- [ ] Database migrations
- [ ] Monitoring setup
- [ ] Documentation

### 11.5 Demo Requirements
- [ ] Working demo showing: query → retrieval → generation → RAGAS evaluation
- [ ] Real-time metrics display
- [ ] Safety system demonstration
- [ ] Performance benchmarks
- [ ] Multilingual query examples

## 12. Implementation Timeline

### Phase 1: Core RAG System (Week 1-2)
- Document ingestion pipeline
- Embedding and vector storage
- Basic query processing
- GPT-4o-mini integration

### Phase 2: RAGAS Integration (Week 3)
- RAGAS evaluation pipeline
- Quality gate implementation
- Metrics storage
- Real-time evaluation

### Phase 3: Safety & Monitoring (Week 4)
- Safety system implementation
- Monitoring dashboard
- Alerting system
- Performance optimization

### Phase 4: Production Deployment (Week 5)
- Containerization
- Environment setup
- Testing and validation
- Documentation and demo

## 13. Cursor AI Implementation Instructions

When implementing this system:

1. **Start with the core RAG pipeline** - Focus on getting document ingestion, embedding generation, and basic query processing working first
2. **Use the exact models specified** - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 for embeddings and gpt-4o-mini for generation
3. **Implement RAGAS evaluation early** - Build the evaluation system alongside the RAG pipeline, not as an afterthought
4. **Follow the safety-first approach** - Implement quality gates and safety checks at every step
5. **Use the provided schemas** - Follow the exact database schemas and API specifications provided
6. **Implement comprehensive logging** - Every component should have detailed logging for debugging and monitoring
7. **Write tests from the beginning** - Don't leave testing until the end; implement unit tests alongside each component
8. **Use Docker from day one** - Set up the containerized environment early to avoid deployment issues
9. **Focus on performance** - Keep the p95 < 3 seconds requirement in mind throughout development
10. **Document everything** - Maintain clear documentation for all components and APIs

This PRD provides the complete specification for building a production-ready medical AI assistant with RAGAS evaluation. Follow the technical specifications exactly and implement the safety measures rigorously.