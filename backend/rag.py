import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict
from embedder import TitanEmbedder

class RAGSystem:
    def __init__(self, kb_path: str = "kb/knowledge.txt", chroma_path: str = "chroma_db"):
        """Initialize RAG system with ChromaDB and Titan embeddings"""
        self.kb_path = kb_path
        self.chroma_path = chroma_path
        self.embedder = TitanEmbedder()
        self.collection_name = "knowledge_base"
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        
        # Initialize or load collection
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or load ChromaDB collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection with {self.collection.count()} documents")
        except:
            # Create new collection if it doesn't exist
            print("Creating new collection...")
            self.collection = self.client.create_collection(name=self.collection_name)
            self._load_knowledge_base()
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk size
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if len(c) > 20]  # Filter out very small chunks
    
    def _load_knowledge_base(self):
        """Load and process knowledge base into ChromaDB"""
        print("Loading knowledge base...")
        
        if not os.path.exists(self.kb_path):
            print(f"Warning: Knowledge base file not found at {self.kb_path}")
            return
        
        # Read knowledge base
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Chunk the text
        chunks = self._chunk_text(text)
        print(f"Created {len(chunks)} chunks from knowledge base")
        
        if len(chunks) == 0:
            print("Warning: No chunks created from knowledge base")
            return
        
        # Generate embeddings using Titan
        print("Generating embeddings...")
        embeddings = self.embedder.embed_batch(chunks)
        
        # Store in ChromaDB
        print("Storing in ChromaDB...")
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
        
        print(f"Successfully loaded {len(chunks)} chunks into ChromaDB")
    
    def query_chroma(self, question: str, top_k: int = 3) -> List[str]:
        """
        Query ChromaDB for relevant context
        
        Args:
            question: User's question
            top_k: Number of top results to return
            
        Returns:
            List of relevant text chunks
        """
        # Generate embedding for the question
        question_embedding = self.embedder.embed_text(question)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        
        # Extract documents
        documents = results['documents'][0] if results['documents'] else []
        
        return documents
    
    def build_prompt(self, context: List[str], question: str) -> str:
        """
        Build a prompt for the LLM using retrieved context
        
        Args:
            context: List of relevant text chunks
            question: User's question
            
        Returns:
            Formatted prompt string
        """
        context_text = "\n\n".join(context) if context else "No relevant context found."
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question. If the context doesn't contain relevant information, say so politely.

Context:
{context_text}

Question: {question}

Answer: """
        
        return prompt
    
    def load_chroma(self):
        """Public method to reload the ChromaDB collection"""
        self._initialize_collection()
