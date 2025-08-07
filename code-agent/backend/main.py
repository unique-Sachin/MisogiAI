from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
import logging
import json
import asyncio
from models import ChatRequest, ChatResponse
from graph import CodeAgentGraph

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Code Agent Backend",
    description="LangGraph-powered coding assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the graph
try:
    agent_graph = CodeAgentGraph()
    logger.info("Code Agent Graph initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Code Agent Graph: {str(e)}")
    agent_graph = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Code Agent Backend is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    openai_key_available = bool(os.getenv("OPENAI_API_KEY"))
    graph_initialized = agent_graph is not None
    
    return {
        "status": "healthy" if openai_key_available and graph_initialized else "unhealthy",
        "openai_key_configured": openai_key_available,
        "graph_initialized": graph_initialized,
        "dependencies": {
            "openai": "✓" if openai_key_available else "✗",
            "langgraph": "✓" if graph_initialized else "✗"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages through the LangGraph
    """
    try:
        if not agent_graph:
            raise HTTPException(
                status_code=500, 
                detail="Code Agent Graph not initialized. Check server logs."
            )
        
        if not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        logger.info(f"Processing chat request: {request.message[:50]}...")
        
        # Process the message through the graph
        result_state = await agent_graph.process_message(
            user_input=request.message,
            conversation_id=request.conversation_id
        )
        
        response = ChatResponse(
            response=result_state.final_response,
            conversation_id=result_state.conversation_id,
            status="success"
        )
        
        logger.info(f"Successfully processed chat request for conversation {result_state.conversation_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint that provides real-time responses
    """
    try:
        if not agent_graph:
            raise HTTPException(
                status_code=500, 
                detail="Code Agent Graph not initialized. Check server logs."
            )
        
        if not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        logger.info(f"Processing streaming chat request: {request.message[:50]}...")
        
        async def generate_stream():
            try:
                # Process the message through the graph
                result_state = await agent_graph.process_message(
                    user_input=request.message,
                    conversation_id=request.conversation_id
                )
                
                response_text = result_state.final_response
                conversation_id = result_state.conversation_id
                
                # Simulate streaming by sending chunks of the response
                words = response_text.split()
                chunk_size = 3  # Send 3 words at a time
                
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = " " + " ".join(chunk_words)
                    
                    # If it's the first chunk, don't add leading space
                    if i == 0:
                        chunk_text = chunk_text.lstrip()
                    
                    data = {
                        "content": chunk_text,
                        "conversation_id": conversation_id,
                        "status": "streaming"
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Small delay to simulate real streaming
                    await asyncio.sleep(0.05)
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
                logger.info(f"Successfully streamed chat response for conversation {conversation_id}")
                
            except Exception as e:
                logger.error(f"Error in streaming generation: {str(e)}")
                error_data = {
                    "content": f"Error: {str(e)}",
                    "status": "error"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history (placeholder for future implementation)
    """
    # In a real implementation, you'd retrieve from a database
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "status": "not_implemented"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "localhost")
    
    logger.info(f"Starting Code Agent Backend on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
