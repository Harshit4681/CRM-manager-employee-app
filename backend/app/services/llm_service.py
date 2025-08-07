import asyncio
import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import tiktoken

import openai
from openai import AsyncOpenAI

from app.models.schemas import (
    DocumentInfo, ParsedQuery, SearchResult, Decision, 
    DecisionReasoning, QueryIntent
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-powered document analysis and decision making"""
    
    def __init__(self):
        self.client = None
        self.tokenizer = None
        self.max_context_tokens = 6000  # Leave room for response
        
    async def initialize(self):
        """Initialize LLM service"""
        try:
            logger.info("Initializing LLM service...")
            
            # Initialize OpenAI client
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Initialize tokenizer for token counting
            try:
                self.tokenizer = tiktoken.encoding_for_model(settings.OPENAI_MODEL)
            except Exception as e:
                logger.warning(f"Could not load tokenizer: {e}")
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            logger.info("LLM service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLM service: {e}")
            raise
    
    async def analyze_documents(
        self,
        query: str,
        parsed_query: ParsedQuery,
        documents: List[DocumentInfo],
        search_results: List[SearchResult]
    ) -> List[Decision]:
        """
        Analyze documents and make decisions based on query
        
        Args:
            query: Original natural language query
            parsed_query: Parsed query with intent and entities
            documents: List of processed documents
            search_results: Relevant chunks from vector search
            
        Returns:
            List of decisions for each document
        """
        try:
            logger.info(f"Analyzing {len(documents)} documents for query intent: {parsed_query.intent}")
            
            decisions = []
            
            for document in documents:
                try:
                    # Get relevant chunks for this document
                    doc_chunks = [
                        result for result in search_results 
                        if result.document_id == document.document_id
                    ]
                    
                    # Analyze document
                    decision = await self._analyze_single_document(
                        query, parsed_query, document, doc_chunks
                    )
                    
                    decisions.append(decision)
                    
                except Exception as e:
                    logger.error(f"Error analyzing document {document.document_id}: {e}")
                    # Create error decision
                    error_decision = Decision(
                        decision_id=str(uuid.uuid4()),
                        document_id=document.document_id,
                        document_name=document.filename,
                        decision="error",
                        reasoning=DecisionReasoning(
                            relevant_clauses=[],
                            evidence=[f"Error analyzing document: {str(e)}"],
                            confidence_score=0.0,
                            reasoning_steps=["Document analysis failed"]
                        ),
                        key_factors=["analysis_error"],
                        recommendations=["Please try again or contact support"]
                    )
                    decisions.append(error_decision)
            
            logger.info(f"Completed analysis of {len(documents)} documents")
            return decisions
            
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return []
    
    async def _analyze_single_document(
        self,
        query: str,
        parsed_query: ParsedQuery,
        document: DocumentInfo,
        relevant_chunks: List[SearchResult]
    ) -> Decision:
        """Analyze a single document and make a decision"""
        
        # Build context from relevant chunks
        context = self._build_context(document, relevant_chunks)
        
        # Create prompt based on query intent
        prompt = self._create_analysis_prompt(query, parsed_query, document, context)
        
        # Get LLM response
        response = await self._call_llm(prompt)
        
        # Parse response into decision
        decision = self._parse_llm_response(response, document)
        
        return decision
    
    def _build_context(self, document: DocumentInfo, relevant_chunks: List[SearchResult]) -> str:
        """Build context from relevant document chunks"""
        context_parts = []
        
        # Document metadata
        context_parts.append(f"Document: {document.filename}")
        context_parts.append(f"Type: {document.document_type}")
        context_parts.append(f"Total chunks: {len(document.chunks)}")
        context_parts.append("")
        
        # Relevant chunks (sorted by relevance score)
        sorted_chunks = sorted(relevant_chunks, key=lambda x: x.score, reverse=True)
        
        for i, chunk in enumerate(sorted_chunks[:10]):  # Limit to top 10 chunks
            context_parts.append(f"--- Relevant Section {i+1} (Score: {chunk.score:.3f}) ---")
            if chunk.page_number:
                context_parts.append(f"Page: {chunk.page_number}")
            if chunk.section:
                context_parts.append(f"Section: {chunk.section}")
            context_parts.append(chunk.content)
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if self.tokenizer:
            tokens = self.tokenizer.encode(context)
            if len(tokens) > self.max_context_tokens:
                # Truncate to fit within token limit
                truncated_tokens = tokens[:self.max_context_tokens]
                context = self.tokenizer.decode(truncated_tokens)
                context += "\n\n[Context truncated due to length]"
        
        return context
    
    def _create_analysis_prompt(
        self,
        query: str,
        parsed_query: ParsedQuery,
        document: DocumentInfo,
        context: str
    ) -> str:
        """Create analysis prompt based on query intent"""
        
        base_prompt = f"""You are an expert document analyst specializing in insurance and policy documents. 
Analyze the provided document content and answer the user's query with detailed reasoning.

USER QUERY: {query}

QUERY INTENT: {parsed_query.intent.value}
EXTRACTED ENTITIES: {json.dumps(parsed_query.entities, indent=2)}
KEYWORDS: {', '.join(parsed_query.keywords)}

DOCUMENT CONTEXT:
{context}

"""
        
        # Add intent-specific instructions
        if parsed_query.intent == QueryIntent.POLICY_SEARCH:
            base_prompt += self._get_policy_search_instructions()
        elif parsed_query.intent == QueryIntent.CLAIM_VALIDATION:
            base_prompt += self._get_claim_validation_instructions()
        elif parsed_query.intent == QueryIntent.COVERAGE_CHECK:
            base_prompt += self._get_coverage_check_instructions()
        elif parsed_query.intent == QueryIntent.PREMIUM_CALCULATION:
            base_prompt += self._get_premium_calculation_instructions()
        else:
            base_prompt += self._get_general_analysis_instructions()
        
        base_prompt += self._get_response_format_instructions()
        
        return base_prompt
    
    def _get_policy_search_instructions(self) -> str:
        return """
TASK: Search for and identify relevant policy information.

Focus on:
1. Policy terms and conditions that match the query
2. Coverage details and limits
3. Eligibility criteria
4. Premium structure
5. Key benefits and exclusions

"""
    
    def _get_claim_validation_instructions(self) -> str:
        return """
TASK: Validate if a claim is eligible based on policy terms.

Consider:
1. Whether the condition/incident is covered
2. If all eligibility criteria are met
3. Any waiting periods or restrictions
4. Required documentation
5. Exclusions that might apply

Provide clear ELIGIBLE, NOT_ELIGIBLE, or REQUIRES_REVIEW decision.

"""
    
    def _get_coverage_check_instructions(self) -> str:
        return """
TASK: Check what is covered under the policy.

Analyze:
1. Specific coverage for the queried condition/scenario
2. Coverage limits and sub-limits
3. Deductibles and co-payments
4. Geographic coverage
5. Time-based restrictions

"""
    
    def _get_premium_calculation_instructions(self) -> str:
        return """
TASK: Analyze premium calculation factors and provide estimates.

Consider:
1. Age-based premium factors
2. Location-based adjustments
3. Coverage amount multipliers
4. Risk assessment factors
5. Available discounts

Note: Provide ranges or factors rather than exact amounts unless explicitly stated in the document.

"""
    
    def _get_general_analysis_instructions(self) -> str:
        return """
TASK: Provide general analysis and extract relevant information.

Focus on:
1. Key information relevant to the query
2. Important terms and conditions
3. Notable benefits or restrictions
4. Recommendations based on the content

"""
    
    def _get_response_format_instructions(self) -> str:
        return """
RESPONSE FORMAT:
Provide your analysis in the following JSON format:

{
    "decision": "eligible|not_eligible|partial|requires_review|information_found|not_applicable",
    "confidence_score": 0.85,
    "reasoning_steps": [
        "Step 1: Analyzed policy terms for...",
        "Step 2: Found relevant clause stating...",
        "Step 3: Evaluated eligibility criteria..."
    ],
    "relevant_clauses": [
        "Specific policy text or clause 1",
        "Specific policy text or clause 2"
    ],
    "evidence": [
        "Evidence point 1 supporting the decision",
        "Evidence point 2 supporting the decision"
    ],
    "key_factors": [
        "Factor 1 that influenced the decision",
        "Factor 2 that influenced the decision"
    ],
    "recommendations": [
        "Recommendation 1 for the user",
        "Recommendation 2 for the user"
    ]
}

IMPORTANT:
- Be specific and cite exact policy text when possible
- Provide confidence score between 0.0 and 1.0
- Include step-by-step reasoning
- Make evidence-based decisions
- Be transparent about limitations or uncertainties
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with the analysis prompt"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance document analyst. Provide accurate, evidence-based analysis with clear reasoning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Return fallback response
            return json.dumps({
                "decision": "error",
                "confidence_score": 0.0,
                "reasoning_steps": [f"LLM analysis failed: {str(e)}"],
                "relevant_clauses": [],
                "evidence": ["Unable to analyze due to LLM error"],
                "key_factors": ["llm_error"],
                "recommendations": ["Please try again or contact support"]
            })
    
    def _parse_llm_response(self, response: str, document: DocumentInfo) -> Decision:
        """Parse LLM response into Decision object"""
        try:
            # Parse JSON response
            response_data = json.loads(response)
            
            # Create DecisionReasoning
            reasoning = DecisionReasoning(
                relevant_clauses=response_data.get("relevant_clauses", []),
                evidence=response_data.get("evidence", []),
                confidence_score=float(response_data.get("confidence_score", 0.0)),
                reasoning_steps=response_data.get("reasoning_steps", [])
            )
            
            # Create Decision
            decision = Decision(
                decision_id=str(uuid.uuid4()),
                document_id=document.document_id,
                document_name=document.filename,
                decision=response_data.get("decision", "unknown"),
                reasoning=reasoning,
                key_factors=response_data.get("key_factors", []),
                recommendations=response_data.get("recommendations", [])
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Create fallback decision
            return Decision(
                decision_id=str(uuid.uuid4()),
                document_id=document.document_id,
                document_name=document.filename,
                decision="error",
                reasoning=DecisionReasoning(
                    relevant_clauses=[],
                    evidence=[f"Failed to parse LLM response: {str(e)}"],
                    confidence_score=0.0,
                    reasoning_steps=["Response parsing failed"]
                ),
                key_factors=["parsing_error"],
                recommendations=["Please try again"]
            )
    
    async def summarize_documents(self, documents: List[DocumentInfo]) -> str:
        """Create a summary of multiple documents"""
        try:
            # Build context from all documents
            context_parts = []
            for doc in documents:
                context_parts.append(f"Document: {doc.filename}")
                # Include first few chunks for summary
                for chunk in doc.chunks[:3]:
                    context_parts.append(chunk.content[:500])
                context_parts.append("")
            
            context = "\n".join(context_parts)
            
            prompt = f"""Provide a concise summary of the following documents:

{context}

Create a summary that highlights:
1. Main topics covered
2. Key policies or terms
3. Important coverage details
4. Notable exclusions or limitations

Keep the summary under 500 words."""
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at summarizing insurance and policy documents."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing documents: {e}")
            return f"Unable to generate summary: {str(e)}"
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback estimation
        return len(text) // 4
    
    async def close(self):
        """Cleanup LLM service resources"""
        logger.info("LLM service closed")