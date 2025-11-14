from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import json
import os
from dotenv import load_dotenv
from rag import RAGSystem

# Load environment variables from .env file
load_dotenv(dotenv_path="../.env")

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock = boto3.client(
    "bedrock-runtime", 
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

# Initialize RAG system
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    print("Initializing RAG system...")
    rag_system = RAGSystem()
    print("RAG system initialized successfully")

# Request/Response models
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    context: list = []

class HealthResponse(BaseModel):
    status: str

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that performs RAG and invokes Bedrock NovaLite
    
    Args:
        request: ChatRequest containing the user's question
        
    Returns:
        ChatResponse with the answer and context used
    """
    try:
        # Validate request
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"\nReceived question: {request.question}")
        
        # Step 1: Retrieve relevant context from ChromaDB
        print("Querying ChromaDB for context...")
        context = rag_system.query_chroma(request.question, top_k=3)
        print(f"Retrieved {len(context)} context chunks")
        
        # Step 2: Build prompt with context
        prompt = rag_system.build_prompt(context, request.question)
        print("Built prompt for Bedrock")
        
        # Step 3: Invoke Bedrock NovaLite
        print("Invoking Bedrock NovaLite...")
        
        # Prepare the request body for Nova Lite
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        response = bedrock.invoke_model(
            modelId="us.amazon.nova-lite-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract the answer from Nova's response format
        answer = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
        
        if not answer:
            # Fallback for different response formats
            answer = response_body.get('completion', 'Sorry, I could not generate a response.')
        
        print(f"Generated answer: {answer[:100]}...")
        
        return ChatResponse(
            answer=answer.strip(),
            context=context
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/reload-kb")
async def reload_knowledge_base():
    """Reload the knowledge base (useful after updating knowledge.txt)"""
    try:
        global rag_system
        print("Reloading knowledge base...")
        rag_system = RAGSystem()
        return {"status": "success", "message": "Knowledge base reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading knowledge base: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
