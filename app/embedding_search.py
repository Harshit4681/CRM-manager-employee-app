import numpy as np
import faiss
import logging
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import pickle
import os
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingSearch:
    """
    Semantic search using sentence transformers and FAISS vector database
    """
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.chunks = []
        self.metadata = []
        
    async def create_embeddings(self, processed_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create embeddings for document chunks and build FAISS index
        
        Args:
            processed_doc: Processed document with chunks
            
        Returns:
            Vector store information
        """
        try:
            chunks = processed_doc["chunks"]
            logger.info(f"Creating embeddings for {len(chunks)} chunks")
            
            # Generate embeddings for all chunks
            embeddings = self.model.encode(chunks, show_progress_bar=True)
            embeddings = np.array(embeddings).astype('float32')
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            self.index.add(embeddings)
            
            # Store chunks and metadata
            self.chunks = chunks
            self.metadata = [
                {
                    "chunk_id": i,
                    "chunk_text": chunk,
                    "document_url": processed_doc["url"],
                    "document_type": processed_doc["type"]
                }
                for i, chunk in enumerate(chunks)
            ]
            
            vector_store = {
                "index": self.index,
                "chunks": self.chunks,
                "metadata": self.metadata,
                "embedding_model": settings.EMBEDDING_MODEL,
                "total_vectors": len(chunks)
            }
            
            logger.info(f"Successfully created FAISS index with {len(chunks)} vectors")
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Embedding creation failed: {str(e)}")
    
    async def search_similar(self, query: str, vector_store: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic similarity
        
        Args:
            query: Search query
            vector_store: Vector store with index and metadata
            
        Returns:
            List of relevant chunks with similarity scores
        """
        try:
            logger.info(f"Searching for query: {query}")
            
            # Encode query
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, settings.TOP_K_RESULTS)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= settings.SIMILARITY_THRESHOLD:
                    result = {
                        "chunk_text": self.chunks[idx],
                        "similarity_score": float(score),
                        "chunk_id": idx,
                        "rank": i + 1,
                        "metadata": self.metadata[idx]
                    }
                    results.append(result)
            
            logger.info(f"Found {len(results)} relevant chunks above threshold")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise Exception(f"Similarity search failed: {str(e)}")
    
    def save_index(self, file_path: str):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{file_path}.faiss")
            
            # Save metadata
            with open(f"{file_path}_metadata.pkl", 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.metadata
                }, f)
            
            logger.info(f"Index saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise Exception(f"Index saving failed: {str(e)}")
    
    def load_index(self, file_path: str):
        """Load FAISS index and metadata from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{file_path}.faiss")
            
            # Load metadata
            with open(f"{file_path}_metadata.pkl", 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
            
            logger.info(f"Index loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise Exception(f"Index loading failed: {str(e)}")
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the current embedding index"""
        if self.index is None:
            return {"status": "no_index", "total_vectors": 0}
        
        return {
            "status": "ready",
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "embedding_model": settings.EMBEDDING_MODEL,
            "total_chunks": len(self.chunks)
        }
    
    async def batch_search(self, queries: List[str], vector_store: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search for multiple queries
        
        Args:
            queries: List of search queries
            vector_store: Vector store with index and metadata
            
        Returns:
            List of results for each query
        """
        try:
            logger.info(f"Performing batch search for {len(queries)} queries")
            
            results = []
            for query in queries:
                query_results = await self.search_similar(query, vector_store)
                results.append(query_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch search: {str(e)}")
            raise Exception(f"Batch search failed: {str(e)}")
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank search results based on additional criteria
        
        Args:
            query: Original search query
            results: Initial search results
            
        Returns:
            Re-ranked results
        """
        # Simple re-ranking based on text length and similarity score
        # Can be enhanced with more sophisticated ranking algorithms
        
        def ranking_score(result):
            similarity = result["similarity_score"]
            text_length = len(result["chunk_text"])
            
            # Prefer chunks with good similarity and reasonable length
            length_score = min(text_length / 1000, 1.0)  # Normalize to 0-1
            combined_score = similarity * 0.8 + length_score * 0.2
            
            return combined_score
        
        # Sort by combined ranking score
        reranked = sorted(results, key=ranking_score, reverse=True)
        
        # Update rank information
        for i, result in enumerate(reranked):
            result["rerank"] = i + 1
        
        return reranked