import boto3
import json
import os
from typing import List

class TitanEmbedder:
    def __init__(self, region_name: str = None):
        """Initialize Bedrock client for Titan Embeddings"""
        # Use environment variable or default to us-east-1 (where Bedrock models are available)
        region = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )
        # Updated model ID format for Titan Embeddings V2
        self.model_id = "amazon.titan-embed-text-v2:0"
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for a single text using Amazon Titan Embeddings
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            return embedding
        
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
