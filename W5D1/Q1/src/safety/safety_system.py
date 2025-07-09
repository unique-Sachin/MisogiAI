"""Multi-layer safety system for medical AI assistant."""

import os
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class QueryClassification(BaseModel):
    """Classification result for medical queries."""
    is_medical_query: bool = Field(description="Whether this is a medical query")
    is_harmful: bool = Field(description="Whether this query could be harmful")
    query_type: str = Field(description="Type of query: information, diagnosis, treatment, etc.")
    risk_level: str = Field(description="Risk level: low, medium, high")
    reasoning: str = Field(description="Reasoning for the classification")


class ResponseSafety(BaseModel):
    """Safety assessment for responses."""
    is_safe: bool = Field(description="Whether the response is safe")
    contains_diagnosis: bool = Field(description="Whether response contains diagnosis")
    contains_treatment: bool = Field(description="Whether response contains treatment advice")
    safety_concerns: List[str] = Field(description="List of safety concerns")
    recommendations: List[str] = Field(description="Recommendations for improvement")


class MedicalSafetySystem:
    """Multi-layer safety system for medical AI responses."""
    
    def __init__(self):
        try:
            self.llm = ChatOpenAI(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                temperature=0.1
            )
            self.harm_classifier = self._create_harm_classifier()
            self.response_safety_checker = self._create_response_safety_checker()
            self.enabled = True
        except Exception as e:
            print(f"Warning: Could not initialize safety system: {e}")
            self.enabled = False
    
    def _create_harm_classifier(self) -> LLMChain:
        """Create LangChain-based harm classifier."""
        
        parser = PydanticOutputParser(pydantic_object=QueryClassification)
        
        prompt = PromptTemplate(
            template="""You are a medical safety classifier. Analyze the following query for safety concerns:
            
            Query: {query}
            
            Classify this query based on:
            1. Is it a legitimate medical information request?
            2. Could it be harmful if answered directly?
            3. What type of medical query is this?
            4. What's the risk level?
            5. Provide reasoning for your classification
            
            Guidelines:
            - "information" queries are generally safe (asking about conditions, symptoms, general info)
            - "diagnosis" queries are high risk (asking for personal medical diagnosis)
            - "treatment" queries are high risk (asking for specific medical treatment)
            - "medication" queries asking for dosages or prescriptions are high risk
            - General educational queries about medical topics are usually low risk
            
            {format_instructions}
            """,
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return LLMChain(llm=self.llm, prompt=prompt, output_parser=parser)
    
    def _create_response_safety_checker(self) -> LLMChain:
        """Create response safety checker."""
        
        parser = PydanticOutputParser(pydantic_object=ResponseSafety)
        
        prompt = PromptTemplate(
            template="""Analyze this medical AI response for safety concerns:
            
            Original Query: {query}
            AI Response: {response}
            
            Check for:
            1. Direct medical advice or diagnosis
            2. Treatment recommendations
            3. Medication dosages or prescriptions
            4. Harmful or dangerous information
            5. Inappropriate medical claims
            6. Statements that could replace professional medical advice
            
            Guidelines:
            - Responses should be educational and informational only
            - Should not provide personal medical diagnosis
            - Should not recommend specific treatments
            - Should include disclaimers about consulting healthcare professionals
            - Should cite sources when making medical claims
            
            {format_instructions}
            """,
            input_variables=["query", "response"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        return LLMChain(llm=self.llm, prompt=prompt, output_parser=parser)
    
    def validate_query(self, query: str) -> Dict:
        """Validate query using safety classifier."""
        
        if not self.enabled:
            return {"is_safe": True, "classification": None, "block_reason": None}
        
        try:
            classification = self.harm_classifier.run(query=query)
            
            # Determine if query should be blocked
            should_block = (
                classification.is_harmful or
                classification.query_type in ["diagnosis", "treatment", "medication"] or
                classification.risk_level == "high"
            )
            
            return {
                "is_safe": not should_block,
                "classification": classification.dict(),
                "block_reason": self._get_block_reason(classification) if should_block else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Default to blocking on error for safety
            return {
                "is_safe": False,
                "classification": None,
                "block_reason": f"Safety classification failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_response(self, query: str, response: str, ragas_scores: Dict) -> Dict:
        """Validate response using safety checker and RAGAS thresholds."""
        
        if not self.enabled:
            return {
                "is_safe": True,
                "safety_assessment": None,
                "quality_gate_passed": True,
                "block_reason": None
            }
        
        try:
            # Check RAGAS thresholds (critical for medical use)
            faithfulness_threshold = float(os.getenv("RAGAS_FAITHFULNESS_THRESHOLD", "0.90"))
            precision_threshold = float(os.getenv("RAGAS_CONTEXT_PRECISION_THRESHOLD", "0.85"))
            
            faithfulness_passed = ragas_scores.get("faithfulness", 0) >= faithfulness_threshold
            precision_passed = ragas_scores.get("context_precision", 0) >= precision_threshold
            
            # Content safety check
            safety_assessment = self.response_safety_checker.run(
                query=query, 
                response=response
            )
            
            # Overall safety decision
            is_safe = (
                safety_assessment.is_safe and
                faithfulness_passed and
                precision_passed
            )
            
            quality_gate_passed = faithfulness_passed and precision_passed
            
            block_reasons = []
            if not faithfulness_passed:
                block_reasons.append(f"Low faithfulness score: {ragas_scores.get('faithfulness', 0):.3f} < {faithfulness_threshold}")
            if not precision_passed:
                block_reasons.append(f"Low context precision: {ragas_scores.get('context_precision', 0):.3f} < {precision_threshold}")
            if not safety_assessment.is_safe:
                block_reasons.extend(safety_assessment.safety_concerns)
            
            return {
                "is_safe": is_safe,
                "safety_assessment": safety_assessment.dict(),
                "quality_gate_passed": quality_gate_passed,
                "faithfulness_passed": faithfulness_passed,
                "precision_passed": precision_passed,
                "block_reason": "; ".join(block_reasons) if block_reasons else None,
                "ragas_scores": ragas_scores,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Default to unsafe on error
            return {
                "is_safe": False,
                "safety_assessment": None,
                "quality_gate_passed": False,
                "block_reason": f"Safety validation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_block_reason(self, classification: QueryClassification) -> str:
        """Get human-readable block reason."""
        reasons = []
        
        if classification.is_harmful:
            reasons.append("Query identified as potentially harmful")
        
        if classification.query_type in ["diagnosis", "treatment", "medication"]:
            reasons.append(f"Query type '{classification.query_type}' requires professional medical consultation")
        
        if classification.risk_level == "high":
            reasons.append("Query classified as high risk")
        
        if classification.reasoning:
            reasons.append(f"Reasoning: {classification.reasoning}")
        
        return "; ".join(reasons) if reasons else "Query blocked for safety reasons"
    
    def get_safety_disclaimer(self) -> str:
        """Get standard safety disclaimer for medical responses."""
        return (
            "⚠️ MEDICAL DISCLAIMER: This information is for educational purposes only and "
            "should not replace professional medical advice. Always consult with a qualified "
            "healthcare provider for medical diagnosis, treatment, or medication decisions."
        )
    
    def audit_log(self, event_type: str, query: str, result: Dict, user_id: Optional[str] = None) -> Dict:
        """Create audit log entry."""
        return {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "query": query,
            "result": result,
            "system_version": "1.0.0"
        }


class SafetyException(Exception):
    """Exception raised for safety violations."""
    pass


class QueryBlockedException(SafetyException):
    """Exception raised when a query is blocked for safety reasons."""
    pass


class ResponseBlockedException(SafetyException):
    """Exception raised when a response is blocked for safety reasons."""
    pass 