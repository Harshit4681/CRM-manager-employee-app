import re
import logging
from typing import List, Dict, Any
import tiktoken

logger = logging.getLogger(__name__)

class TextProcessor:
    """Utility class for text processing and chunking"""
    
    def __init__(self):
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoder: {e}")
            self.tokenizer = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines but preserve paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Fix common encoding issues
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--') # Em dash
        text = text.replace('\u2026', '...') # Horizontal ellipsis
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'^Page \d+.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Strip and normalize
        text = text.strip()
        
        return text
    
    def split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            chunk_size: Target size in characters (or tokens if tokenizer available)
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Use token-based chunking if tokenizer is available
        if self.tokenizer:
            return self._split_by_tokens(text, chunk_size, chunk_overlap)
        else:
            return self._split_by_characters(text, chunk_size, chunk_overlap)
    
    def _split_by_tokens(self, text: str, max_tokens: int, overlap_tokens: int) -> List[str]:
        """Split text by token count"""
        try:
            tokens = self.tokenizer.encode(text)
            
            if len(tokens) <= max_tokens:
                return [text]
            
            chunks = []
            start_idx = 0
            
            while start_idx < len(tokens):
                # Get chunk tokens
                end_idx = min(start_idx + max_tokens, len(tokens))
                chunk_tokens = tokens[start_idx:end_idx]
                
                # Decode back to text
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                # Try to end at sentence boundary if not at the end
                if end_idx < len(tokens):
                    chunk_text = self._adjust_chunk_boundary(chunk_text)
                
                chunks.append(chunk_text.strip())
                
                # Move start position with overlap
                if end_idx == len(tokens):
                    break
                start_idx = end_idx - overlap_tokens
            
            return chunks
            
        except Exception as e:
            logger.warning(f"Token-based splitting failed: {e}, falling back to character-based")
            return self._split_by_characters(text, max_tokens * 4, overlap_tokens * 4)  # Rough conversion
    
    def _split_by_characters(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text by character count"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            # Calculate end index
            end_idx = min(start_idx + chunk_size, len(text))
            
            # Get chunk
            chunk = text[start_idx:end_idx]
            
            # Try to end at sentence boundary if not at the end
            if end_idx < len(text):
                chunk = self._adjust_chunk_boundary(chunk)
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            if end_idx == len(text):
                break
            start_idx = end_idx - chunk_overlap
        
        return chunks
    
    def _adjust_chunk_boundary(self, chunk: str) -> str:
        """Adjust chunk boundary to end at sentence or paragraph break"""
        # Try to end at paragraph break
        last_para = chunk.rfind('\n\n')
        if last_para > len(chunk) * 0.5:  # Only if it's in the latter half
            return chunk[:last_para]
        
        # Try to end at sentence break
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        best_pos = -1
        
        for ending in sentence_endings:
            pos = chunk.rfind(ending)
            if pos > len(chunk) * 0.5:  # Only if it's in the latter half
                best_pos = max(best_pos, pos + len(ending) - 1)
        
        if best_pos > -1:
            return chunk[:best_pos + 1]
        
        # Try to end at word boundary
        last_space = chunk.rfind(' ')
        if last_space > len(chunk) * 0.8:  # Only if it's near the end
            return chunk[:last_space]
        
        # Return as-is if no good boundary found
        return chunk
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        # In production, you might want to use more sophisticated NLP libraries
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
            'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my',
            'one', 'all', 'would', 'there', 'their', 'what', 'so',
            'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me'
        }
        
        # Filter out stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def detect_sections(self, text: str) -> List[Dict[str, Any]]:
        """Detect sections/headings in text"""
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Simple heuristics for section detection
            is_section = (
                # All caps with reasonable length
                (line.isupper() and 5 <= len(line) <= 100) or
                # Starts with number and period
                re.match(r'^\d+\.', line) or
                # Common section patterns
                re.match(r'^(Chapter|Section|Article|Part)\s+\d+', line, re.IGNORECASE) or
                # Short lines that might be headings
                (len(line) < 100 and line.endswith(':')) or
                # Lines with specific formatting
                re.match(r'^[A-Z][A-Z\s]{5,50}$', line)
            )
            
            if is_section:
                sections.append({
                    'title': line,
                    'line_number': i + 1,
                    'start_position': sum(len(lines[j]) + 1 for j in range(i))
                })
        
        return sections
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback: rough estimation (1 token ≈ 4 characters for English)
        return len(text) // 4