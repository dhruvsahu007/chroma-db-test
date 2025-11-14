# RAG Chatbot with AWS Bedrock NovaLite & ChromaDB

A full-stack chatbot application using Retrieval-Augmented Generation (RAG) with AWS Bedrock NovaLite model, ChromaDB vector database, FastAPI backend, and React frontend.

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React + TailwindCSS + Vite
- **LLM**: AWS Bedrock NovaLite
- **Embeddings**: Amazon Titan Embeddings
- **Vector DB**: ChromaDB (local persistent storage)

## 📁 Project Structure

```
project/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── rag.py                 # RAG pipeline implementation
│   ├── embedder.py            # Titan embeddings wrapper
│   ├── requirements.txt       # Python dependencies
│   ├── kb/
│   │   └── knowledge.txt      # Knowledge base (replace with your content)
│   └── chroma_db/             # ChromaDB storage (auto-created)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── ChatBox.jsx    # Chat UI component
    │   ├── App.jsx            # Main app component
    │   ├── main.jsx           # Entry point
    │   └── index.css          # Tailwind styles
    ├── index.html
    ├── package.json
    ├── tailwind.config.js
    ├── postcss.config.js
    └── vite.config.js
```

## 🚀 Setup Instructions

### Prerequisites

1. **AWS Credentials**: Configure your AWS credentials with access to Bedrock
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=ap-south-1
   ```

2. **AWS Bedrock Access**: Ensure you have access to:
   - Amazon Nova Lite model (`us.amazon.nova-lite-v1:0`)
   - Amazon Titan Embeddings (`amazon.titan-embed-text-v1`)

3. **Python 3.8+** and **Node.js 16+** installed

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Replace the knowledge base**:
   - Edit `kb/knowledge.txt` with your actual content
   - This is the text that the chatbot will use to answer questions

5. Start the FastAPI server:
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 🎯 Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Type your question in the input box
3. The chatbot will:
   - Retrieve relevant context from your knowledge base using ChromaDB
   - Send the context + question to AWS Bedrock NovaLite
   - Display the AI-generated response

## 🔄 Updating the Knowledge Base

1. Edit `backend/kb/knowledge.txt` with your new content
2. Restart the backend server (it will automatically re-index on startup)
3. Or call the reload endpoint:
   ```bash
   curl -X POST http://localhost:8000/reload-kb
   ```

## 📡 API Endpoints

### GET /health
Health check endpoint
```bash
curl http://localhost:8000/health
```

### POST /chat
Main chat endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

### POST /reload-kb
Reload knowledge base
```bash
curl -X POST http://localhost:8000/reload-kb
```

## 🛠️ How It Works

1. **Knowledge Base Loading**:
   - On startup, the system reads `kb/knowledge.txt`
   - Chunks the text into manageable pieces
   - Generates embeddings using Amazon Titan
   - Stores embeddings in ChromaDB

2. **Query Processing**:
   - User asks a question
   - System generates an embedding for the question
   - ChromaDB retrieves the most similar text chunks
   - Constructs a prompt with context
   - Sends to AWS Bedrock NovaLite
   - Returns the generated response

3. **RAG Pipeline**:
   ```
   User Question → Embedding → Vector Search → Context Retrieval 
   → Prompt Construction → Bedrock API → Response
   ```

## 🔧 Configuration

### Backend Configuration
Edit values in `backend/app.py` and `backend/embedder.py`:
- AWS Region: `region_name="ap-south-1"`
- Model ID: `modelId="us.amazon.nova-lite-v1:0"`
- Embedding Model: `amazon.titan-embed-text-v1`

### Frontend Configuration
Edit `frontend/src/components/ChatBox.jsx`:
- API URL: `const API_URL = 'http://localhost:8000'`

### RAG Configuration
Edit values in `backend/rag.py`:
- Chunk size: `chunk_size=500`
- Chunk overlap: `overlap=50`
- Top K results: `top_k=3`

## 🐛 Troubleshooting

### Backend Issues

1. **ChromaDB not loading**:
   - Delete the `chroma_db` folder and restart
   - Check that `knowledge.txt` exists and is not empty

2. **AWS Bedrock errors**:
   - Verify AWS credentials: `aws sts get-caller-identity`
   - Check Bedrock model access in AWS Console
   - Ensure you're in a supported region

3. **Import errors**:
   - Make sure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

1. **CORS errors**:
   - Ensure backend is running
   - Check that frontend port matches CORS config in `app.py`

2. **Cannot connect to backend**:
   - Verify backend is running on port 8000
   - Check `API_URL` in `ChatBox.jsx`

## 📦 Production Deployment

For production deployment (e.g., on EC2 with PM2):

1. **Backend**:
   ```bash
   pm2 start "uvicorn app:app --host 0.0.0.0 --port 8000" --name rag-backend
   ```

2. **Frontend**:
   ```bash
   npm run build
   pm2 serve dist 5173 --name rag-frontend
   ```

## 📝 Notes

- The ChromaDB database persists in the `chroma_db` directory
- First run will take longer as it indexes the knowledge base
- Embeddings are generated using Amazon Titan (costs may apply)
- NovaLite model invocations are billed by AWS Bedrock

## 🔐 Security

- Never commit AWS credentials to version control
- Use IAM roles when deploying to EC2
- Consider adding authentication for production use
- Validate and sanitize user inputs

## 📄 License

This project is provided as-is for educational and development purposes.
