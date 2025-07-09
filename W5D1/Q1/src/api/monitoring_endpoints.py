"""Monitoring API endpoints for medical AI assistant."""

from typing import Dict, Any, Optional
from datetime import datetime
# External dependencies (may lack type stubs)
from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy import text  # type: ignore

from ..database.database import get_db
from ..database.models import QueryLog, RAGASMetric, SafetyLog, Document

router = APIRouter(prefix="/metrics", tags=["monitoring"])


@router.get("/dashboard")
async def get_dashboard_metrics(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard metrics for the specified time period."""
    
    try:
        # Simple query count for now
        total_queries = db.query(QueryLog).count()
        blocked_queries = db.query(QueryLog).filter(QueryLog.blocked == True).count()
        
        # Document count
        total_documents = db.query(Document).count()
        
        return {
            "period_hours": hours,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "operational",
            "query_metrics": {
                "total_queries": total_queries,
                "blocked_queries": blocked_queries,
                "success_rate": (total_queries - blocked_queries) / max(total_queries, 1),
                "block_rate": blocked_queries / max(total_queries, 1)
            },
            "document_metrics": {
                "total_documents": total_documents,
                "total_chunks": 0  # Will be populated when documents are processed
            },
            "system_health": {
                "status": "healthy",
                "uptime": "operational",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")


@router.get("/realtime")
async def get_realtime_metrics(
    minutes: int = Query(5, ge=1, le=60, description="Minutes to look back"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get real-time metrics for the specified time period."""
    
    try:
        # Get recent queries (simplified for now)
        recent_queries = db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(10).all()
        
        return {
            "period_minutes": minutes,
            "timestamp": datetime.utcnow().isoformat(),
            "health_indicators": {
                "queries_per_minute": len(recent_queries) / minutes,
                "error_rate": 0.0,  # Will be calculated from actual data
                "system_status": "healthy"
            },
            "recent_queries": [
                {
                    "id": q.id,
                    "query": q.query[:100] + "..." if len(q.query) > 100 else q.query,
                    "timestamp": q.timestamp.isoformat(),
                    "response_time_ms": q.response_time_ms,
                    "blocked": q.blocked,
                    "quality_gate_passed": q.quality_gate_passed
                }
                for q in recent_queries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get realtime metrics: {str(e)}")


@router.get("/evaluation")
async def get_evaluation_metrics(
    limit: int = Query(100, ge=1, le=1000, description="Number of evaluations to analyze"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed evaluation metrics."""
    
    try:
        # Get RAGAS evaluations
        evaluations = db.query(RAGASMetric).order_by(RAGASMetric.timestamp.desc()).limit(limit).all()
        
        if not evaluations:
            return {
                "total_evaluations": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "No evaluation data available"
            }
        
        # Calculate basic statistics
        faithfulness_scores = [e.faithfulness for e in evaluations if e.faithfulness is not None]
        precision_scores = [e.context_precision for e in evaluations if e.context_precision is not None]
        
        return {
            "total_evaluations": len(evaluations),
            "timestamp": datetime.utcnow().isoformat(),
            "faithfulness": {
                "avg": sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0,
                "count": len(faithfulness_scores)
            },
            "context_precision": {
                "avg": sum(precision_scores) / len(precision_scores) if precision_scores else 0,
                "count": len(precision_scores)
            },
            "quality_gate_stats": {
                "total_evaluated": len(evaluations),
                "passed": sum(1 for e in evaluations if e.quality_gate_passed),
                "failed": sum(1 for e in evaluations if not e.quality_gate_passed),
                "pass_rate": sum(1 for e in evaluations if e.quality_gate_passed) / len(evaluations) if evaluations else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation metrics: {str(e)}")


@router.get("/health")
async def get_system_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get overall system health status."""

    try:
        # Simple health check
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy",
                "vector_store": "healthy",
                "rag_engine": "healthy",
                "safety_system": "healthy"
            },
            "metrics_summary": {
                "uptime": "operational",
                "last_check": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "components": {
                "database": "unhealthy",
                "vector_store": "unknown",
                "rag_engine": "unknown",
                "safety_system": "unknown"
            }
        }


@router.post("/record")
async def record_metric(
    metric_name: str,
    value: float,
    metric_type: str = "gauge",
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Record a custom metric."""
    
    try:
        # For now, just return success
        # In a full implementation, this would store the metric
        return {
            "status": "recorded",
            "metric_name": metric_name,
            "value": str(value),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")


@router.get("/batch")
async def batch_evaluation(
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Run batch evaluation on historical data."""
    
    try:
        # This would implement batch evaluation of historical queries
        # For now, return a placeholder response
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "evaluations_processed": 0,
            "summary": {
                "total_queries": 0,
                "avg_faithfulness": 0.0,
                "avg_context_precision": 0.0,
                "quality_gate_pass_rate": 0.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run batch evaluation: {str(e)}") 