"""Database models for medical AI assistant."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()


class Document(Base):
    """Document metadata table."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    title = Column(String)
    content_type = Column(String)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    chunk_count = Column(Integer)
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    error_message = Column(Text)
    doc_metadata = Column(JSON)
    
    # Relationships
    query_logs = relationship("QueryLog", back_populates="document")


class QueryLog(Base):
    """Query logs table."""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, index=True)
    response = Column(Text)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost = Column(Float)
    
    # Document reference
    document_id = Column(Integer, ForeignKey("documents.id"))
    document = relationship("Document", back_populates="query_logs")
    
    # Safety and quality
    blocked = Column(Boolean, default=False)
    block_reason = Column(Text)
    quality_gate_passed = Column(Boolean)
    
    # Relationships
    ragas_metrics = relationship("RAGASMetric", back_populates="query_log")
    safety_logs = relationship("SafetyLog", back_populates="query_log")


class RAGASMetric(Base):
    """RAGAS evaluation metrics table."""
    __tablename__ = "ragas_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, ForeignKey("query_logs.id"))
    
    # Core RAGAS metrics
    context_precision = Column(Float)
    context_recall = Column(Float)
    faithfulness = Column(Float)
    answer_relevancy = Column(Float)
    
    # Quality gates
    quality_gate_passed = Column(Boolean)
    faithfulness_passed = Column(Boolean)
    precision_passed = Column(Boolean)
    
    # Metadata
    evaluation_time_ms = Column(Integer)
    evaluation_error = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query_log = relationship("QueryLog", back_populates="ragas_metrics")


class SafetyLog(Base):
    """Safety system logs table."""
    __tablename__ = "safety_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, ForeignKey("query_logs.id"))
    
    # Query safety
    query_is_safe = Column(Boolean)
    query_classification = Column(JSON)
    query_block_reason = Column(Text)
    
    # Response safety
    response_is_safe = Column(Boolean)
    response_safety_assessment = Column(JSON)
    response_block_reason = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query_log = relationship("QueryLog", back_populates="safety_logs")


class SystemMetric(Base):
    """System-wide metrics table."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    metric_type = Column(String)  # gauge, counter, histogram
    timestamp = Column(DateTime, default=datetime.utcnow)
    sys_metadata = Column(JSON)


# Pydantic models for API responses
class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    content_type: str
    file_size: int
    upload_date: datetime
    processed_date: Optional[datetime]
    chunk_count: Optional[int]
    status: str
    error_message: Optional[str]
    doc_metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class QueryLogResponse(BaseModel):
    id: int
    query: str
    response: str
    user_id: Optional[str]
    timestamp: datetime
    response_time_ms: int
    tokens_used: int
    cost: float
    blocked: bool
    block_reason: Optional[str]
    quality_gate_passed: Optional[bool]
    
    class Config:
        from_attributes = True


class RAGASMetricResponse(BaseModel):
    id: int
    query_log_id: int
    context_precision: Optional[float]
    context_recall: Optional[float]
    faithfulness: Optional[float]
    answer_relevancy: Optional[float]
    quality_gate_passed: Optional[bool]
    faithfulness_passed: Optional[bool]
    precision_passed: Optional[bool]
    evaluation_time_ms: Optional[int]
    evaluation_error: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SafetyLogResponse(BaseModel):
    id: int
    query_log_id: int
    query_is_safe: Optional[bool]
    query_classification: Optional[Dict[str, Any]]
    query_block_reason: Optional[str]
    response_is_safe: Optional[bool]
    response_safety_assessment: Optional[Dict[str, Any]]
    response_block_reason: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SystemMetricResponse(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    metric_type: str
    timestamp: datetime
    sys_metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True 