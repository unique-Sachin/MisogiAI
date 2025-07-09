import os
from typing import Dict, List, Optional
import time

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain_community.vectorstores.chroma import Chroma

from .embeddings import CustomSentenceTransformerEmbeddings

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Import RAGAS evaluator
try:
    from ..evaluation.ragas_evaluator import MedicalRAGASEvaluator, QualityGate
    RAGAS_AVAILABLE = True
except ImportError:
    print("Warning: RAGAS evaluation not available")
    RAGAS_AVAILABLE = False

# Import safety system
try:
    from ..safety.safety_system import MedicalSafetySystem
    SAFETY_AVAILABLE = True
except ImportError:
    print("Warning: Safety system not available")
    SAFETY_AVAILABLE = False


class MedicalRAGEngine:
    """High-level interface for querying the vector store with GPT-4o-mini."""

    def __init__(self, persist_directory: str | None = None, enable_ragas: bool = True, enable_safety: bool = True):
        # Use environment variable or default
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./medical_vector_db")
        
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        self.embeddings = CustomSentenceTransformerEmbeddings(embedding_model)
        self.vector_store = Chroma(
            embedding_function=self.embeddings, 
            persist_directory=persist_directory
        )

        self.llm = ChatOpenAI(
            model=llm_model, 
            temperature=0.1, 
            max_tokens=1000
        )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )

        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a medical knowledge assistant.\n"
                "Provide accurate, evidence-based information using only the provided context.\n"
                "Always cite sources and indicate when information is outside your knowledge.\n"
                "Never provide direct medical advice or diagnosis.\n"
                "Always include appropriate disclaimers about consulting healthcare professionals.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Comprehensive answer:"
            ),
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True,
        )
        
        # Initialize RAGAS evaluator if available
        self.enable_ragas = enable_ragas and RAGAS_AVAILABLE
        if self.enable_ragas:
            try:
                self.ragas_evaluator = MedicalRAGASEvaluator()
                self.quality_gate = QualityGate()
                print("✅ RAGAS evaluation enabled")
            except Exception as e:
                print(f"Warning: Could not initialize RAGAS evaluator: {e}")
                self.enable_ragas = False
        else:
            self.ragas_evaluator = None
            self.quality_gate = None
        
        # Initialize safety system if available
        self.enable_safety = enable_safety and SAFETY_AVAILABLE
        if self.enable_safety:
            try:
                self.safety_system = MedicalSafetySystem()
                print("✅ Safety system enabled")
            except Exception as e:
                print(f"Warning: Could not initialize safety system: {e}")
                self.enable_safety = False
        else:
            self.safety_system = None

    def query(self, user_query: str, user_id: Optional[str] = None) -> Dict:
        """Run the RAG pipeline for the supplied query and return answer + sources."""
        start_time = time.time()
        
        # Step 1: Query safety validation
        query_safety = {"is_safe": True, "block_reason": None}
        if self.enable_safety and self.safety_system:
            query_safety = self.safety_system.validate_query(user_query)
            if not query_safety["is_safe"]:
                return {
                    "query": user_query,
                    "answer": f"Query blocked for safety reasons: {query_safety['block_reason']}",
                    "sources": [],
                    "tokens_used": 0,
                    "cost": 0.0,
                    "ragas_scores": {},
                    "quality_gate_passed": False,
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "safety_status": query_safety,
                    "blocked": True
                }
        
        # Step 2: Generate response
        with get_openai_callback() as cb:
            result = self.qa_chain.invoke({"query": user_query})
            answer = result["result"]
            source_documents = result["source_documents"]

            sources: List[Dict] = []
            context_texts: List[str] = []
            
            for doc in source_documents:
                sources.append(
                    {
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", "Unknown"),
                        "content": doc.page_content[:200] + "...",
                    }
                )
                context_texts.append(doc.page_content)

            # Step 3: Run RAGAS evaluation if enabled
            ragas_scores = {}
            quality_gate_passed = True
            
            if self.enable_ragas and self.ragas_evaluator:
                try:
                    ragas_scores = self.ragas_evaluator.evaluate_response(
                        query=user_query,
                        context=context_texts,
                        response=answer
                    )
                    quality_gate_passed = ragas_scores.get("quality_gate_passed", True)
                except Exception as e:
                    print(f"Warning: RAGAS evaluation failed: {e}")
                    ragas_scores = {
                        "context_precision": 0.0,
                        "context_recall": 0.0,
                        "faithfulness": 0.0,
                        "answer_relevancy": 0.0,
                        "quality_gate_passed": False,
                        "error": str(e)
                    }
                    quality_gate_passed = False

            # Step 4: Response safety validation
            response_safety = {"is_safe": True, "block_reason": None}
            if self.enable_safety and self.safety_system:
                response_safety = self.safety_system.validate_response(
                    user_query, answer, ragas_scores
                )
                if not response_safety["is_safe"]:
                    return {
                        "query": user_query,
                        "answer": f"Response blocked for safety reasons: {response_safety['block_reason']}",
                        "sources": sources,
                        "tokens_used": cb.total_tokens,
                        "cost": cb.total_cost,
                        "ragas_scores": ragas_scores,
                        "quality_gate_passed": False,
                        "response_time_ms": int((time.time() - start_time) * 1000),
                        "safety_status": response_safety,
                        "blocked": True
                    }

            # Step 5: Add safety disclaimer if enabled
            if self.enable_safety and self.safety_system:
                disclaimer = self.safety_system.get_safety_disclaimer()
                answer = f"{answer}\n\n{disclaimer}"

            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "query": user_query,
                "answer": answer,
                "sources": sources,
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost,
                "ragas_scores": ragas_scores,
                "quality_gate_passed": quality_gate_passed,
                "response_time_ms": response_time_ms,
                "safety_status": {
                    "query_safety": query_safety,
                    "response_safety": response_safety
                },
                "blocked": False,
                "context": context_texts  # Include for debugging/monitoring
            } 