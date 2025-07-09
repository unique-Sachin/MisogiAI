"""Monitoring metrics for medical AI assistant."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Integer

from ..database.models import QueryLog, RAGASMetric, SafetyLog, SystemMetric, Document
from ..database.database import get_db


class MetricsCollector:
    """Collect and aggregate metrics for monitoring."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_dashboard_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard metrics for the last N hours."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Query metrics
        total_queries = self.db.query(QueryLog).filter(
            QueryLog.timestamp >= since
        ).count()
        
        blocked_queries = self.db.query(QueryLog).filter(
            QueryLog.timestamp >= since,
            QueryLog.blocked == True
        ).count()
        
        # RAGAS metrics
        ragas_stats = self.db.query(
            func.avg(RAGASMetric.faithfulness).label('avg_faithfulness'),
            func.avg(RAGASMetric.context_precision).label('avg_precision'),
            func.avg(RAGASMetric.context_recall).label('avg_recall'),
            func.avg(RAGASMetric.answer_relevancy).label('avg_relevancy'),
            func.count(RAGASMetric.quality_gate_passed).label('total_evaluated'),
            func.sum(func.cast(RAGASMetric.quality_gate_passed, Integer)).label('quality_gate_passed')
        ).join(QueryLog).filter(
            QueryLog.timestamp >= since
        ).first()
        
        # Performance metrics
        performance_stats = self.db.query(
            func.avg(QueryLog.response_time_ms).label('avg_response_time'),
            func.avg(QueryLog.tokens_used).label('avg_tokens'),
            func.avg(QueryLog.cost).label('avg_cost')
        ).filter(
            QueryLog.timestamp >= since
        ).first()
        
        # Safety metrics
        safety_stats = self.db.query(
            func.count(SafetyLog.id).label('total_safety_checks'),
            func.sum(func.cast(SafetyLog.query_is_safe, Integer)).label('safe_queries'),
            func.sum(func.cast(SafetyLog.response_is_safe, Integer)).label('safe_responses')
        ).join(QueryLog).filter(
            QueryLog.timestamp >= since
        ).first()
        
        # Document metrics
        document_stats = self.db.query(
            func.count(Document.id).label('total_documents'),
            func.sum(Document.chunk_count).label('total_chunks')
        ).first()
        
        return {
            "period_hours": hours,
            "timestamp": datetime.utcnow().isoformat(),
            "query_metrics": {
                "total_queries": total_queries,
                "blocked_queries": blocked_queries,
                "success_rate": (total_queries - blocked_queries) / max(total_queries, 1),
                "block_rate": blocked_queries / max(total_queries, 1)
            },
            "ragas_metrics": {
                "avg_faithfulness": float(ragas_stats.avg_faithfulness or 0) if ragas_stats else 0,
                "avg_context_precision": float(ragas_stats.avg_precision or 0) if ragas_stats else 0,
                "avg_context_recall": float(ragas_stats.avg_recall or 0) if ragas_stats else 0,
                "avg_answer_relevancy": float(ragas_stats.avg_relevancy or 0) if ragas_stats else 0,
                "total_evaluated": ragas_stats.total_evaluated or 0 if ragas_stats else 0,
                "quality_gate_pass_rate": (ragas_stats.quality_gate_passed or 0) / max(ragas_stats.total_evaluated or 1, 1) if ragas_stats else 0
            },
            "performance_metrics": {
                "avg_response_time_ms": float(performance_stats.avg_response_time or 0) if performance_stats else 0,
                "avg_tokens_used": float(performance_stats.avg_tokens or 0) if performance_stats else 0,
                "avg_cost": float(performance_stats.avg_cost or 0) if performance_stats else 0
            },
            "safety_metrics": {
                "total_safety_checks": safety_stats.total_safety_checks or 0 if safety_stats else 0,
                "safe_queries": safety_stats.safe_queries or 0 if safety_stats else 0,
                "safe_responses": safety_stats.safe_responses or 0 if safety_stats else 0,
                "query_safety_rate": (safety_stats.safe_queries or 0) / max(safety_stats.total_safety_checks or 1, 1) if safety_stats else 0,
                "response_safety_rate": (safety_stats.safe_responses or 0) / max(safety_stats.total_safety_checks or 1, 1) if safety_stats else 0
            },
            "document_metrics": {
                "total_documents": document_stats.total_documents or 0 if document_stats else 0,
                "total_chunks": document_stats.total_chunks or 0 if document_stats else 0
            }
        }
    
    def get_realtime_metrics(self, minutes: int = 5) -> Dict[str, Any]:
        """Get real-time metrics for the last N minutes."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Recent queries
        recent_queries = self.db.query(QueryLog).filter(
            QueryLog.timestamp >= since
        ).order_by(desc(QueryLog.timestamp)).limit(10).all()
        
        # Recent failures
        recent_failures = self.db.query(QueryLog).filter(
            QueryLog.timestamp >= since,
            QueryLog.blocked == True
        ).order_by(desc(QueryLog.timestamp)).limit(5).all()
        
        # System health indicators
        total_recent = len(recent_queries)
        blocked_recent = len(recent_failures)
        
        return {
            "period_minutes": minutes,
            "timestamp": datetime.utcnow().isoformat(),
            "health_indicators": {
                "queries_per_minute": total_recent / minutes,
                "error_rate": blocked_recent / max(total_recent, 1),
                "avg_response_time": sum(q.response_time_ms for q in recent_queries) / max(total_recent, 1),
                "system_status": "healthy" if blocked_recent / max(total_recent, 1) < 0.1 else "warning"
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
            ],
            "recent_failures": [
                {
                    "id": f.id,
                    "query": f.query[:100] + "..." if len(f.query) > 100 else f.query,
                    "timestamp": f.timestamp.isoformat(),
                    "block_reason": f.block_reason
                }
                for f in recent_failures
            ]
        }
    
    def get_evaluation_metrics(self, limit: int = 100) -> Dict[str, Any]:
        """Get detailed evaluation metrics."""
        
        # Get recent RAGAS evaluations
        recent_evaluations = self.db.query(RAGASMetric).join(QueryLog).order_by(
            desc(RAGASMetric.timestamp)
        ).limit(limit).all()
        
        # Calculate distribution statistics
        if recent_evaluations:
            faithfulness_scores = [e.faithfulness for e in recent_evaluations if e.faithfulness is not None]
            precision_scores = [e.context_precision for e in recent_evaluations if e.context_precision is not None]
            recall_scores = [e.context_recall for e in recent_evaluations if e.context_recall is not None]
            relevancy_scores = [e.answer_relevancy for e in recent_evaluations if e.answer_relevancy is not None]
            
            def calculate_percentiles(scores: List[float]) -> Dict[str, float]:
                if not scores:
                    return {"p50": 0, "p95": 0, "p99": 0}
                scores_sorted = sorted(scores)
                n = len(scores_sorted)
                return {
                    "p50": scores_sorted[int(n * 0.5)],
                    "p95": scores_sorted[int(n * 0.95)],
                    "p99": scores_sorted[int(n * 0.99)]
                }
            
            return {
                "total_evaluations": len(recent_evaluations),
                "timestamp": datetime.utcnow().isoformat(),
                "faithfulness": {
                    "avg": sum(faithfulness_scores) / max(len(faithfulness_scores), 1),
                    "min": min(faithfulness_scores) if faithfulness_scores else 0,
                    "max": max(faithfulness_scores) if faithfulness_scores else 0,
                    **calculate_percentiles(faithfulness_scores)
                },
                "context_precision": {
                    "avg": sum(precision_scores) / max(len(precision_scores), 1),
                    "min": min(precision_scores) if precision_scores else 0,
                    "max": max(precision_scores) if precision_scores else 0,
                    **calculate_percentiles(precision_scores)
                },
                "context_recall": {
                    "avg": sum(recall_scores) / max(len(recall_scores), 1),
                    "min": min(recall_scores) if recall_scores else 0,
                    "max": max(recall_scores) if recall_scores else 0,
                    **calculate_percentiles(recall_scores)
                },
                "answer_relevancy": {
                    "avg": sum(relevancy_scores) / max(len(relevancy_scores), 1),
                    "min": min(relevancy_scores) if relevancy_scores else 0,
                    "max": max(relevancy_scores) if relevancy_scores else 0,
                    **calculate_percentiles(relevancy_scores)
                },
                "quality_gate_stats": {
                    "total_evaluated": len(recent_evaluations),
                    "passed": sum(1 for e in recent_evaluations if e.quality_gate_passed),
                    "failed": sum(1 for e in recent_evaluations if not e.quality_gate_passed),
                    "pass_rate": sum(1 for e in recent_evaluations if e.quality_gate_passed) / max(len(recent_evaluations), 1)
                }
            }
        else:
            return {
                "total_evaluations": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "No evaluation data available"
            }
    
    def record_system_metric(self, metric_name: str, value: float, metric_type: str = "gauge", metadata: Optional[Dict] = None):
        """Record a system metric."""
        metric = SystemMetric(
            metric_name=metric_name,
            metric_value=value,
            metric_type=metric_type,
            metadata=metadata or {}
        )
        self.db.add(metric)
        self.db.commit()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        # Get recent metrics
        dashboard_metrics = self.get_dashboard_metrics(hours=1)
        realtime_metrics = self.get_realtime_metrics(minutes=5)
        
        # Determine health status
        error_rate = dashboard_metrics["query_metrics"]["block_rate"]
        avg_response_time = dashboard_metrics["performance_metrics"]["avg_response_time_ms"]
        quality_gate_pass_rate = dashboard_metrics["ragas_metrics"]["quality_gate_pass_rate"]
        
        # Health thresholds
        health_status = "healthy"
        issues = []
        
        if error_rate > 0.1:
            health_status = "warning"
            issues.append(f"High error rate: {error_rate:.2%}")
        
        if avg_response_time > 5000:
            health_status = "warning"
            issues.append(f"High response time: {avg_response_time:.0f}ms")
        
        if quality_gate_pass_rate < 0.8:
            health_status = "critical"
            issues.append(f"Low quality gate pass rate: {quality_gate_pass_rate:.2%}")
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "issues": issues,
            "metrics_summary": {
                "error_rate": error_rate,
                "avg_response_time_ms": avg_response_time,
                "quality_gate_pass_rate": quality_gate_pass_rate,
                "queries_per_minute": realtime_metrics["health_indicators"]["queries_per_minute"]
            }
        }


def get_metrics_collector(db: Session = next(get_db())) -> MetricsCollector:
    """Get metrics collector instance."""
    return MetricsCollector(db) 