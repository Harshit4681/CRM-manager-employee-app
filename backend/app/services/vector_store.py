import asyncio
import logging
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
import json
import pickle
import os
from datetime import datetime

# Vector store imports
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone not available, using FAISS only")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available")

from sentence_transformers import SentenceTransformer
import openai

from app.models.schemas import DocumentChunk, SearchResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for vector storage and semantic search"""
    
    def __init__(self):
        self.pinecone_client = None
        self.pinecone_index = None
        self.faiss_index = None
        self.faiss_metadata = {}
        self.embedding_model = None
        self.openai_client = None
        self.dimension = settings.PINECONE_DIMENSION
        
    async def initialize(self):
        """Initialize vector store services"""
        try:
            logger.info("Initializing vector store...")
            
            # Initialize OpenAI client for embeddings
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Initialize Pinecone if available
            if PINECONE_AVAILABLE and settings.PINECONE_API_KEY:
                await self._initialize_pinecone()
            
            # Initialize FAISS as backup
            if FAISS_AVAILABLE:
                await self._initialize_faiss()
            
            # Initialize local embedding model as backup
            await self._initialize_local_embeddings()
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    async def _initialize_pinecone(self):
        """Initialize Pinecone vector database"""
        try:
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            # Create index if it doesn't exist
            index_name = settings.PINECONE_INDEX_NAME
            if index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {index_name}")
                pinecone.create_index(
                    name=index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
            
            self.pinecone_index = pinecone.Index(index_name)
            logger.info("Pinecone initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Pinecone: {e}")
            self.pinecone_index = None
    
    async def _initialize_faiss(self):
        """Initialize FAISS vector index"""
        try:
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            
            # Try to load existing index
            index_path = "faiss_index.bin"
            metadata_path = "faiss_metadata.json"
            
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                self.faiss_index = faiss.read_index(index_path)
                with open(metadata_path, 'r') as f:
                    self.faiss_metadata = json.load(f)
                logger.info("Loaded existing FAISS index")
            else:
                logger.info("Created new FAISS index")
                
        except Exception as e:
            logger.warning(f"Failed to initialize FAISS: {e}")
            self.faiss_index = None
    
    async def _initialize_local_embeddings(self):
        """Initialize local embedding model as backup"""
        try:
            # Use a lightweight but effective model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Local embedding model initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize local embedding model: {e}")
            self.embedding_model = None
    
    async def store_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Store document chunks in vector database"""
        try:
            if not chunks:
                return True
            
            logger.info(f"Storing {len(chunks)} chunks in vector database")
            
            # Generate embeddings for all chunks
            embeddings = await self._generate_embeddings([chunk.content for chunk in chunks])
            
            # Store in Pinecone if available
            if self.pinecone_index:
                await self._store_chunks_pinecone(chunks, embeddings)
            
            # Store in FAISS if available
            if self.faiss_index is not None:
                await self._store_chunks_faiss(chunks, embeddings)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing chunks: {e}")
            return False
    
    async def _store_chunks_pinecone(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """Store chunks in Pinecone"""
        try:
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                vector = {
                    'id': chunk.chunk_id,
                    'values': embedding,
                    'metadata': {
                        'document_id': chunk.metadata.get('document_id', ''),
                        'content': chunk.content[:1000],  # Truncate for metadata
                        'page_number': chunk.page_number,
                        'section': chunk.section,
                        'chunk_index': chunk.metadata.get('chunk_index', 0),
                        'created_at': datetime.utcnow().isoformat()
                    }
                }
                vectors.append(vector)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.pinecone_index.upsert(vectors=batch)
            
            logger.info(f"Stored {len(chunks)} chunks in Pinecone")
            
        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {e}")
            raise
    
    async def _store_chunks_faiss(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """Store chunks in FAISS"""
        try:
            # Convert embeddings to numpy array
            embedding_matrix = np.array(embeddings, dtype=np.float32)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embedding_matrix)
            
            # Add to index
            start_id = self.faiss_index.ntotal
            self.faiss_index.add(embedding_matrix)
            
            # Store metadata
            for i, chunk in enumerate(chunks):
                vector_id = start_id + i
                self.faiss_metadata[str(vector_id)] = {
                    'chunk_id': chunk.chunk_id,
                    'document_id': chunk.metadata.get('document_id', ''),
                    'content': chunk.content,
                    'page_number': chunk.page_number,
                    'section': chunk.section,
                    'chunk_index': chunk.metadata.get('chunk_index', 0),
                    'created_at': datetime.utcnow().isoformat()
                }
            
            # Save index and metadata
            await self._save_faiss_index()
            
            logger.info(f"Stored {len(chunks)} chunks in FAISS")
            
        except Exception as e:
            logger.error(f"Error storing chunks in FAISS: {e}")
            raise
    
    async def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search for similar chunks"""
        try:
            logger.info(f"Searching for: {query[:100]}...")
            
            # Generate query embedding
            query_embeddings = await self._generate_embeddings([query])
            query_embedding = query_embeddings[0]
            
            results = []
            
            # Search in Pinecone first (preferred)
            if self.pinecone_index:
                results = await self._search_pinecone(
                    query_embedding, document_ids, top_k, similarity_threshold
                )
            
            # Fallback to FAISS if no Pinecone results
            if not results and self.faiss_index is not None:
                results = await self._search_faiss(
                    query_embedding, document_ids, top_k, similarity_threshold
                )
            
            logger.info(f"Found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    async def _search_pinecone(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]],
        top_k: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Search in Pinecone"""
        try:
            # Build filter
            filter_dict = {}
            if document_ids:
                filter_dict['document_id'] = {'$in': document_ids}
            
            # Query Pinecone
            response = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            results = []
            for match in response.matches:
                if match.score >= similarity_threshold:
                    metadata = match.metadata
                    result = SearchResult(
                        chunk_id=match.id,
                        document_id=metadata.get('document_id', ''),
                        content=metadata.get('content', ''),
                        score=float(match.score),
                        page_number=metadata.get('page_number'),
                        section=metadata.get('section'),
                        metadata=metadata
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    async def _search_faiss(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]],
        top_k: int,
        similarity_threshold: float
    ) -> List[SearchResult]:
        """Search in FAISS"""
        try:
            # Convert to numpy and normalize
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.faiss_index.search(query_vector, min(top_k * 2, self.faiss_index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1 or score < similarity_threshold:
                    continue
                
                metadata = self.faiss_metadata.get(str(idx))
                if not metadata:
                    continue
                
                # Filter by document IDs if specified
                if document_ids and metadata.get('document_id') not in document_ids:
                    continue
                
                result = SearchResult(
                    chunk_id=metadata['chunk_id'],
                    document_id=metadata['document_id'],
                    content=metadata['content'],
                    score=float(score),
                    page_number=metadata.get('page_number'),
                    section=metadata.get('section'),
                    metadata=metadata
                )
                results.append(result)
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            return []
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            # Try OpenAI embeddings first (preferred)
            if self.openai_client:
                try:
                    response = await self.openai_client.embeddings.create(
                        model=settings.EMBEDDING_MODEL,
                        input=texts
                    )
                    return [data.embedding for data in response.data]
                except Exception as e:
                    logger.warning(f"OpenAI embeddings failed: {e}, falling back to local model")
            
            # Fallback to local model
            if self.embedding_model:
                embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
                return embeddings.tolist()
            
            raise Exception("No embedding service available")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def _save_faiss_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.faiss_index is not None:
                faiss.write_index(self.faiss_index, "faiss_index.bin")
                
                with open("faiss_metadata.json", 'w') as f:
                    json.dump(self.faiss_metadata, f)
                    
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            # Delete from Pinecone
            if self.pinecone_index:
                # Query all chunks for this document
                response = self.pinecone_index.query(
                    vector=[0.0] * self.dimension,  # Dummy vector
                    top_k=10000,  # Get all
                    include_metadata=True,
                    filter={'document_id': document_id}
                )
                
                chunk_ids = [match.id for match in response.matches]
                if chunk_ids:
                    self.pinecone_index.delete(ids=chunk_ids)
            
            # Delete from FAISS (rebuild index without these chunks)
            if self.faiss_index is not None:
                # Remove metadata entries
                keys_to_remove = []
                for key, metadata in self.faiss_metadata.items():
                    if metadata.get('document_id') == document_id:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.faiss_metadata[key]
                
                # Save updated metadata
                await self._save_faiss_index()
            
            logger.info(f"Deleted document {document_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        stats = {
            'pinecone_available': self.pinecone_index is not None,
            'faiss_available': self.faiss_index is not None,
            'local_embeddings_available': self.embedding_model is not None,
            'total_vectors': 0
        }
        
        if self.pinecone_index:
            try:
                index_stats = self.pinecone_index.describe_index_stats()
                stats['pinecone_vectors'] = index_stats.total_vector_count
                stats['total_vectors'] += index_stats.total_vector_count
            except:
                stats['pinecone_vectors'] = 0
        
        if self.faiss_index is not None:
            stats['faiss_vectors'] = self.faiss_index.ntotal
            if not self.pinecone_index:  # Only count FAISS if Pinecone is not available
                stats['total_vectors'] += self.faiss_index.ntotal
        
        return stats
    
    async def close(self):
        """Cleanup vector store resources"""
        try:
            # Save FAISS index one final time
            if self.faiss_index is not None:
                await self._save_faiss_index()
            
            logger.info("Vector store closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing vector store: {e}")