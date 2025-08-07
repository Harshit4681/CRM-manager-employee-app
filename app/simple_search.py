import logging
from typing import List, Dict, Any
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class SimpleSearch:
    """
    Simple text-based search using keyword matching and basic similarity
    """
    
    def __init__(self):
        pass
    
    async def create_embeddings(self, processed_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create simple text index"""
        chunks = processed_doc["chunks"]
        
        # Create keyword index
        keyword_index = {}
        for i, chunk in enumerate(chunks):
            words = self._extract_keywords(chunk)
            for word in words:
                if word not in keyword_index:
                    keyword_index[word] = []
                keyword_index[word].append(i)
        
        vector_store = {
            "chunks": chunks,
            "keyword_index": keyword_index,
            "metadata": processed_doc.get("metadata", {}),
            "total_vectors": len(chunks)
        }
        
        logger.info(f"Created keyword index with {len(chunks)} chunks and {len(keyword_index)} keywords")
        return vector_store
    
    async def search_similar(self, query: str, vector_store: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for similar chunks using keyword matching"""
        chunks = vector_store["chunks"]
        keyword_index = vector_store["keyword_index"]
        
        query_keywords = self._extract_keywords(query)
        chunk_scores = {}
        
        # Score chunks based on keyword matches
        for keyword in query_keywords:
            if keyword in keyword_index:
                for chunk_idx in keyword_index[keyword]:
                    if chunk_idx not in chunk_scores:
                        chunk_scores[chunk_idx] = 0
                    chunk_scores[chunk_idx] += 1
        
        # Add text similarity scores
        for i, chunk in enumerate(chunks):
            text_sim = self._text_similarity(query.lower(), chunk.lower())
            if i in chunk_scores:
                chunk_scores[i] += text_sim * 2  # Weight text similarity higher
            elif text_sim > 0.3:  # Threshold for text similarity
                chunk_scores[i] = text_sim
        
        # Sort by score and return top results
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for i, (chunk_idx, score) in enumerate(sorted_chunks[:5]):
            if score > 0:
                result = {
                    "chunk_text": chunks[chunk_idx],
                    "similarity_score": min(score / 10, 1.0),  # Normalize score
                    "chunk_id": chunk_idx,
                    "rank": i + 1,
                    "metadata": {"chunk_id": chunk_idx}
                }
                results.append(result)
        
        logger.info(f"Found {len(results)} relevant chunks for query: {query[:50]}...")
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter out common stop words and short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        keywords = []
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _find_relevant_chunks_by_keywords(self, query: str, chunks: List[str]) -> List[Dict[str, Any]]:
        """Find chunks containing query keywords"""
        query_lower = query.lower()
        query_words = self._extract_keywords(query_lower)
        
        results = []
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = 0
            
            # Count keyword matches
            for word in query_words:
                if word in chunk_lower:
                    score += chunk_lower.count(word)
            
            # Add similarity bonus
            similarity = self._text_similarity(query_lower, chunk_lower)
            score += similarity * 5
            
            if score > 0:
                results.append({
                    "chunk_text": chunk,
                    "similarity_score": min(score / 10, 1.0),
                    "chunk_id": i,
                    "rank": 0,  # Will be set later
                    "metadata": {"chunk_id": i}
                })
        
        # Sort by score and assign ranks
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results[:5]  # Return top 5 results