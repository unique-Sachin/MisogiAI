"""RAGAS Evaluation System for Medical AI Assistant."""

import os
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime

from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)
from ragas import evaluate
from langchain_openai import ChatOpenAI

# Try to import LangchainLLM, fallback if not available
try:
    from ragas.llms import LangchainLLM
except ImportError:
    print("Warning: LangchainLLM not available, using default RAGAS models")
    LangchainLLM = None

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class MedicalRAGASEvaluator:
    """RAGAS evaluator for medical AI responses with quality gates."""
    
    def __init__(self):
        self.metrics = [context_precision, context_recall, faithfulness, answer_relevancy]
        
        # Quality gate thresholds from PRD
        self.faithfulness_threshold = float(os.getenv("RAGAS_FAITHFULNESS_THRESHOLD", "0.90"))
        self.context_precision_threshold = float(os.getenv("RAGAS_CONTEXT_PRECISION_THRESHOLD", "0.85"))
        
        # Configure RAGAS to use GPT-4o-mini
        self._configure_ragas_models()
        
    def _configure_ragas_models(self):
        """Configure RAGAS to use our LangChain models."""
        try:
            if LangchainLLM is not None:
                # Use our LangChain ChatOpenAI instance
                llm = ChatOpenAI(
                    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                    temperature=0.1
                )
                langchain_llm = LangchainLLM(llm=llm)
                
                # Configure metrics to use our LLM
                for metric in self.metrics:
                    if hasattr(metric, 'llm'):
                        metric.llm = langchain_llm
            else:
                print("Warning: LangchainLLM not available, using default RAGAS models")
                    
        except Exception as e:
            print(f"Warning: Could not configure RAGAS models: {e}")
            print("RAGAS evaluation may use default models")
    
    def evaluate_response(
        self, 
        query: str, 
        context: List[str], 
        response: str, 
        ground_truth: Optional[str] = None
    ) -> Dict:
        """Evaluate RAG response using RAGAS metrics with LangChain integration."""
        
        try:
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
            
            # Extract scores (handle both single values and arrays)
            scores = {}
            for metric_name in ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]:
                if metric_name in result:
                    value = result[metric_name]
                    # Handle both single values and arrays
                    try:
                        if isinstance(value, (list, pd.Series)) and len(value) > 0:
                            scores[metric_name] = float(value[0])
                        elif hasattr(value, '__iter__') and not isinstance(value, str):
                            # Handle other iterable types
                            scores[metric_name] = float(next(iter(value)))
                        else:
                            scores[metric_name] = float(value)
                    except (ValueError, TypeError, StopIteration):
                        scores[metric_name] = 0.0
                else:
                    scores[metric_name] = 0.0
            
            # Apply quality gates
            quality_gate_passed = (
                scores["faithfulness"] >= self.faithfulness_threshold and
                scores["context_precision"] >= self.context_precision_threshold
            )
            
            return {
                **scores,
                "quality_gate_passed": quality_gate_passed,
                "evaluation_timestamp": datetime.now().isoformat(),
                "faithfulness_threshold": self.faithfulness_threshold,
                "context_precision_threshold": self.context_precision_threshold
            }
            
        except Exception as e:
            # Return default scores if evaluation fails
            print(f"RAGAS evaluation failed: {e}")
            return {
                "context_precision": 0.0,
                "context_recall": 0.0,
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "quality_gate_passed": False,
                "evaluation_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def batch_evaluate(
        self, 
        queries: List[str], 
        contexts: List[List[str]], 
        responses: List[str],
        ground_truths: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Batch evaluation for multiple queries."""
        
        try:
            # Prepare batch dataset
            if ground_truths is None:
                ground_truths = [""] * len(queries)
            
            eval_dataset = {
                "question": queries,
                "answer": responses,
                "contexts": contexts,
                "ground_truth": ground_truths
            }
            
            eval_df = pd.DataFrame(eval_dataset)
            result = evaluate(dataset=eval_df, metrics=self.metrics)
            
            # Add quality gate results
            if isinstance(result, pd.DataFrame):
                result["quality_gate_passed"] = (
                    (result.get("faithfulness", 0) >= self.faithfulness_threshold) &
                    (result.get("context_precision", 0) >= self.context_precision_threshold)
                )
            
            return result
            
        except Exception as e:
            print(f"Batch RAGAS evaluation failed: {e}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                "question", "answer", "contexts", "ground_truth",
                "context_precision", "context_recall", "faithfulness", 
                "answer_relevancy", "quality_gate_passed"
            ])
    
    def get_quality_summary(self, scores: Dict) -> Dict:
        """Get a summary of quality metrics and recommendations."""
        
        summary = {
            "overall_quality": "high" if scores["quality_gate_passed"] else "low",
            "critical_issues": [],
            "recommendations": []
        }
        
        # Check faithfulness (critical for medical use)
        if scores["faithfulness"] < self.faithfulness_threshold:
            summary["critical_issues"].append(
                f"Low faithfulness score ({scores['faithfulness']:.3f} < {self.faithfulness_threshold})"
            )
            summary["recommendations"].append("Review source documents and improve context retrieval")
        
        # Check context precision
        if scores["context_precision"] < self.context_precision_threshold:
            summary["critical_issues"].append(
                f"Low context precision ({scores['context_precision']:.3f} < {self.context_precision_threshold})"
            )
            summary["recommendations"].append("Improve document chunking and retrieval relevance")
        
        # Check other metrics
        if scores["context_recall"] < 0.7:
            summary["recommendations"].append("Increase number of retrieved documents (k parameter)")
        
        if scores["answer_relevancy"] < 0.7:
            summary["recommendations"].append("Improve prompt engineering for better answer relevance")
        
        return summary


class QualityGate:
    """Quality gate system for medical AI responses."""
    
    def __init__(self, min_faithfulness: float = 0.90, min_context_precision: float = 0.85):
        self.min_faithfulness = min_faithfulness
        self.min_context_precision = min_context_precision
    
    def check(self, ragas_scores: Dict) -> bool:
        """Check if response passes quality gates."""
        return (
            ragas_scores.get("faithfulness", 0) >= self.min_faithfulness and
            ragas_scores.get("context_precision", 0) >= self.min_context_precision
        )
    
    def evaluate(self, ragas_scores: Dict) -> Dict:
        """Evaluate scores and return detailed results."""
        passed = self.check(ragas_scores)
        return {
            "quality_gate_passed": passed,
            "faithfulness_passed": ragas_scores.get("faithfulness", 0) >= self.min_faithfulness,
            "precision_passed": ragas_scores.get("context_precision", 0) >= self.min_context_precision,
            "scores": ragas_scores,
            "thresholds": {
                "faithfulness": self.min_faithfulness,
                "context_precision": self.min_context_precision
            }
        }
    
    def get_gate_status(self, ragas_scores: Dict) -> Dict:
        """Get detailed quality gate status."""
        faithfulness_passed = ragas_scores.get("faithfulness", 0) >= self.min_faithfulness
        precision_passed = ragas_scores.get("context_precision", 0) >= self.min_context_precision
        
        return {
            "passed": faithfulness_passed and precision_passed,
            "faithfulness_passed": faithfulness_passed,
            "precision_passed": precision_passed,
            "faithfulness_score": ragas_scores.get("faithfulness", 0),
            "context_precision_score": ragas_scores.get("context_precision", 0),
            "thresholds": {
                "faithfulness": self.min_faithfulness,
                "context_precision": self.min_context_precision
            }
        }


# Exception classes for RAGAS evaluation
class MedicalRAGException(Exception):
    """Base exception for medical RAG system."""
    pass


class RAGASEvaluationError(MedicalRAGException):
    """RAGAS evaluation failed."""
    pass 