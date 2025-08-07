import os
from typing import Dict, Any, Optional, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging
from models import ConversationState

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the state for LangGraph
class GraphState(TypedDict):
    conversation_id: str
    messages: list
    current_step: str
    user_input: str
    processed_input: str
    llm_response: str
    final_response: str
    metadata: dict

class CodeAgentGraph:
    """LangGraph implementation for Code Agent conversation flow"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the conversation flow graph"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("input_node", self.input_node)
        workflow.add_node("processing_node", self.processing_node)
        workflow.add_node("llm_node", self.llm_node)
        workflow.add_node("response_node", self.response_node)
        
        # Define the flow
        workflow.set_entry_point("input_node")
        workflow.add_edge("input_node", "processing_node")
        workflow.add_edge("processing_node", "llm_node")
        workflow.add_edge("llm_node", "response_node")
        workflow.add_edge("response_node", END)
        
        return workflow.compile()
    
    def input_node(self, state: GraphState) -> GraphState:
        """Process and validate user input"""
        logger.info(f"Processing input: {state['user_input']}")
        
        state["current_step"] = "input"
        
        # Basic input validation and sanitization
        if not state["user_input"].strip():
            state["user_input"] = "Hello, I need help with coding."
        
        return state
    
    def processing_node(self, state: GraphState) -> GraphState:
        """Process and enhance user input for better LLM understanding"""
        logger.info("Processing user input for LLM")
        
        state["current_step"] = "processing"
        
        # Add context and structure to the input
        processed_input = self._enhance_input(state["user_input"], state["messages"])
        state["processed_input"] = processed_input
        
        # Add metadata about the conversation
        state["metadata"].update({
            "message_count": len(state["messages"]),
            "processing_timestamp": str(datetime.now()),
            "input_length": len(state["user_input"])
        })
        
        return state
    
    def llm_node(self, state: GraphState) -> GraphState:
        """Generate response using OpenAI GPT-3.5 Turbo"""
        logger.info("Generating LLM response")
        
        state["current_step"] = "llm"
        
        try:
            # Prepare messages for the LLM
            messages = self._prepare_llm_messages(state)
            
            # Call OpenAI API
            response = self.llm.invoke(messages)
            state["llm_response"] = response.content
            
            logger.info("LLM response generated successfully")
            
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            state["llm_response"] = "I'm sorry, I encountered an error while processing your request. Please try again."
        
        return state
    
    def response_node(self, state: GraphState) -> GraphState:
        """Format and finalize the response"""
        logger.info("Formatting final response")
        
        state["current_step"] = "response"
        
        # Post-process the LLM response
        final_response = self._format_response(state["llm_response"])
        state["final_response"] = final_response
        
        return state
    
    def _enhance_input(self, user_input: str, conversation_history: list) -> str:
        """Enhance user input with context and structure"""
        # Add conversation context if available
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]  # Last 4 messages for context
            context = "\\n".join([f"{msg.role}: {msg.content}" for msg in recent_messages])
        
        enhanced_input = f"""
Context from recent conversation:
{context}

Current user message: {user_input}

Please provide a helpful response as a coding assistant. Focus on:
- Clear explanations
- Practical examples
- Best practices
- Step-by-step guidance when appropriate
"""
        return enhanced_input
    
    def _prepare_llm_messages(self, state: GraphState) -> list:
        """Prepare messages for LLM API call"""
        system_message = SystemMessage(content="""
You are a helpful coding assistant called Code Agent. You help developers with:
- Writing and reviewing code
- Debugging and troubleshooting
- Explaining programming concepts
- Suggesting best practices
- Providing step-by-step guidance

Always provide clear, practical, and helpful responses. Use code examples when relevant.
Keep responses concise but comprehensive.
""")
        
        human_message = HumanMessage(content=state["processed_input"])
        
        return [system_message, human_message]
    
    def _format_response(self, llm_response: str) -> str:
        """Format and clean up the LLM response"""
        # Basic cleanup and formatting
        response = llm_response.strip()
        
        # Ensure response isn't too long
        if len(response) > 2000:
            response = response[:1997] + "..."
        
        return response
    
    async def process_message(self, user_input: str, conversation_id: Optional[str] = None) -> ConversationState:
        """Process a user message through the graph"""
        try:
            # Create initial graph state
            graph_state: GraphState = {
                "conversation_id": conversation_id or str(__import__('uuid').uuid4()),
                "messages": [],
                "current_step": "input",
                "user_input": user_input,
                "processed_input": "",
                "llm_response": "",
                "final_response": "",
                "metadata": {}
            }
            
            # Run through the graph
            result = self.graph.invoke(graph_state)
            
            # Convert result back to ConversationState
            final_state = ConversationState.create_new(user_input)
            final_state.conversation_id = result.get('conversation_id', graph_state['conversation_id'])
            final_state.current_step = result.get('current_step', 'completed')
            final_state.processed_input = result.get('processed_input', '')
            final_state.llm_response = result.get('llm_response', '')
            final_state.final_response = result.get('final_response', 'Sorry, I encountered an error.')
            final_state.metadata = result.get('metadata', {})
            
            # Add messages to conversation
            final_state.add_message(user_input, "user")
            final_state.add_message(final_state.final_response, "assistant")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Return error state
            error_state = ConversationState.create_new(user_input)
            error_state.final_response = "I'm sorry, I encountered an error. Please try again."
            return error_state
