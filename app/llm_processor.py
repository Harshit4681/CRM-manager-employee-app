import openai
import logging
import json
from typing import List, Dict, Any, Optional
from app.config import settings
import tiktoken

logger = logging.getLogger(__name__)

class LLMProcessor:
    """
    LLM processor for generating intelligent answers using GPT-4
    """
    
    def __init__(self):
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY or "your-openai-api-key-here"
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    async def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate an intelligent answer using GPT-4 based on relevant document chunks
        
        Args:
            question: The user's question
            relevant_chunks: List of relevant document chunks with metadata
            
        Returns:
            Generated answer string
        """
        try:
            logger.info(f"Generating answer for question: {question[:100]}...")
            
            # Prepare context from relevant chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create the prompt
            prompt = self._create_answer_prompt(question, context)
            
            # Check token limit
            if self._count_tokens(prompt) > self.max_tokens * 0.8:
                logger.warning("Prompt too long, truncating context")
                context = self._truncate_context(context, question)
                prompt = self._create_answer_prompt(question, context)
            
            # Generate answer using OpenAI
            response = await self._call_openai(prompt)
            
            logger.info("Answer generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _prepare_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from relevant chunks"""
        if not relevant_chunks:
            return "No relevant information found in the document."
        
        context_parts = []
        for i, chunk in enumerate(relevant_chunks[:5], 1):  # Limit to top 5 chunks
            chunk_text = chunk.get("chunk_text", "")
            similarity = chunk.get("similarity_score", 0)
            
            context_parts.append(
                f"[Relevant Section {i}] (Relevance: {similarity:.2f})\n{chunk_text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_answer_prompt(self, question: str, context: str) -> str:
        """Create a structured prompt for the LLM"""
        prompt = f"""You are an expert document analyst specialized in insurance, legal, HR, and compliance domains. Your task is to provide accurate, detailed answers based on the provided document context.

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the document context
2. Be specific and cite relevant details from the document
3. If the document doesn't contain enough information to answer the question, state this clearly
4. Provide clear, structured answers that include relevant conditions, limitations, or requirements
5. Focus on accuracy and avoid speculation

DOCUMENT CONTEXT:
{context}

QUESTION: {question}

ANSWER (provide a comprehensive, accurate response based on the document context):"""

        return prompt
    
    def _create_decision_prompt(self, query: str, context: str) -> str:
        """Create a prompt for decision-making scenarios"""
        prompt = f"""You are an expert insurance and legal document analyst. Based on the provided context, analyze the query and provide a structured decision.

CONTEXT FROM DOCUMENT:
{context}

QUERY: {query}

Please analyze this query and provide a response in the following format:
- DECISION: [Approved/Rejected/Requires Review]
- AMOUNT: [If applicable, specify coverage amount or limits]
- JUSTIFICATION: [Detailed explanation referencing specific clauses or conditions from the document]
- RELEVANT_CLAUSES: [List the specific sections or clauses that support this decision]

ANALYSIS:"""

        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Make API call to OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise document analyst that provides accurate answers based strictly on the provided context. You excel at finding specific information in insurance policies, legal documents, and compliance materials."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Fallback response
            return "I apologize, but I'm unable to process this question at the moment due to a technical issue. Please try again later."
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback: rough estimation
            return len(text.split()) * 1.3
    
    def _truncate_context(self, context: str, question: str) -> str:
        """Truncate context to fit within token limits"""
        max_context_tokens = int(self.max_tokens * 0.6)  # Reserve space for question and response
        
        context_tokens = self._count_tokens(context)
        if context_tokens <= max_context_tokens:
            return context
        
        # Simple truncation - can be improved with smarter chunking
        words = context.split()
        target_words = int(len(words) * (max_context_tokens / context_tokens))
        truncated = " ".join(words[:target_words])
        
        return truncated + "\n\n[Note: Context truncated due to length limits]"
    
    async def parse_structured_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query into structured components
        
        Args:
            query: Natural language query (e.g., "46M, knee surgery, Pune, 3-month policy")
            
        Returns:
            Structured query components
        """
        try:
            prompt = f"""Parse the following insurance/medical query into structured components. Extract relevant information such as:
- Age and gender
- Medical procedure/condition
- Location
- Policy details
- Any other relevant information

Query: "{query}"

Please respond with a JSON object containing the extracted information. Use null for missing information.

Example format:
{{
    "age": 46,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Pune",
    "policy_duration": "3 months",
    "policy_type": null,
    "other_details": []
}}

Parsed query:"""

            response = await self._call_openai(prompt)
            
            # Try to parse JSON response
            try:
                parsed = json.loads(response)
                return parsed
            except json.JSONDecodeError:
                # Fallback to simple parsing
                return {"raw_query": query, "parsed": False}
                
        except Exception as e:
            logger.error(f"Error parsing query: {str(e)}")
            return {"raw_query": query, "error": str(e)}
    
    async def generate_structured_response(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a structured JSON response for complex queries
        
        Args:
            question: The user's question
            relevant_chunks: List of relevant document chunks
            
        Returns:
            Structured response with decision, amount, and justification
        """
        try:
            context = self._prepare_context(relevant_chunks)
            prompt = self._create_decision_prompt(question, context)
            
            response = await self._call_openai(prompt)
            
            # Try to extract structured information from response
            structured_response = {
                "question": question,
                "answer": response,
                "decision": self._extract_decision(response),
                "amount": self._extract_amount(response),
                "justification": self._extract_justification(response),
                "relevant_chunks": len(relevant_chunks),
                "confidence": self._calculate_confidence(relevant_chunks)
            }
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "decision": "error",
                "amount": None,
                "justification": str(e),
                "relevant_chunks": 0,
                "confidence": 0.0
            }
    
    def _extract_decision(self, response: str) -> str:
        """Extract decision from LLM response"""
        response_lower = response.lower()
        if "approved" in response_lower:
            return "approved"
        elif "rejected" in response_lower:
            return "rejected"
        elif "covered" in response_lower or "yes" in response_lower:
            return "approved"
        elif "not covered" in response_lower or "no" in response_lower:
            return "rejected"
        else:
            return "requires_review"
    
    def _extract_amount(self, response: str) -> Optional[str]:
        """Extract amount/coverage information from response"""
        import re
        
        # Look for currency amounts
        amount_patterns = [
            r'₹[\d,]+',
            r'\$[\d,]+',
            r'Rs\.?\s*[\d,]+',
            r'amount[:\s]+[\d,]+',
            r'coverage[:\s]+[\d,]+'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_justification(self, response: str) -> str:
        """Extract justification from response"""
        # Look for justification section
        lines = response.split('\n')
        justification_lines = []
        capture = False
        
        for line in lines:
            if 'justification' in line.lower() or 'explanation' in line.lower():
                capture = True
                continue
            elif capture and line.strip():
                justification_lines.append(line.strip())
            elif capture and not line.strip() and justification_lines:
                break
        
        if justification_lines:
            return ' '.join(justification_lines)
        
        # Fallback: return the entire response
        return response
    
    def _calculate_confidence(self, relevant_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not relevant_chunks:
            return 0.0
        
        # Calculate average similarity score
        avg_similarity = sum(chunk.get("similarity_score", 0) for chunk in relevant_chunks) / len(relevant_chunks)
        
        # Adjust confidence based on number of relevant chunks
        chunk_factor = min(len(relevant_chunks) / 3, 1.0)  # Normalize to 0-1
        
        confidence = avg_similarity * 0.8 + chunk_factor * 0.2
        return round(confidence, 2)