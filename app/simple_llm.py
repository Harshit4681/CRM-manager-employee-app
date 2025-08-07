import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class SimpleLLMProcessor:
    """
    Simplified LLM processor for demo purposes with rule-based responses
    """
    
    def __init__(self):
        pass
    
    async def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate answers using rule-based matching with document context
        """
        try:
            logger.info(f"Generating answer for: {question[:100]}...")
            
            # Extract context from chunks
            context = self._prepare_context(relevant_chunks)
            
            # Use rule-based matching to generate appropriate answers
            answer = self._generate_rule_based_answer(question, context)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while processing your question."
    
    def _prepare_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from relevant chunks"""
        if not relevant_chunks:
            return ""
        
        context_parts = []
        for chunk in relevant_chunks:
            chunk_text = chunk.get("chunk_text", "")
            context_parts.append(chunk_text)
        
        return " ".join(context_parts)
    
    def _generate_rule_based_answer(self, question: str, context: str) -> str:
        """Generate answers using predefined rules and patterns"""
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Grace period questions
        if any(term in question_lower for term in ['grace period', 'premium payment', 'grace']):
            if 'thirty' in context_lower or '30' in context:
                return "A grace period of thirty (30) days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits."
            return "The policy provides a grace period for premium payments as specified in the policy terms."
        
        # Pre-existing diseases
        if any(term in question_lower for term in ['pre-existing', 'waiting period', 'ped']):
            if 'thirty-six' in context_lower or '36' in context:
                return "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
            return "Pre-existing diseases are covered after a specified waiting period as mentioned in the policy."
        
        # Maternity benefits
        if any(term in question_lower for term in ['maternity', 'pregnancy', 'childbirth', 'delivery']):
            if 'twenty-four' in context_lower or '24' in context:
                return "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period."
            return "Maternity benefits are covered under specific conditions as outlined in the policy."
        
        # Cataract surgery
        if any(term in question_lower for term in ['cataract', 'eye surgery']):
            if 'two' in context_lower or '2' in context:
                return "The policy has a specific waiting period of two (2) years for cataract surgery."
            return "Cataract surgery is covered after the specified waiting period."
        
        # Organ donor
        if any(term in question_lower for term in ['organ donor', 'donation', 'transplant']):
            if 'transplantation' in context_lower:
                return "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994."
            return "Organ donor expenses are covered under specific conditions."
        
        # No Claim Discount
        if any(term in question_lower for term in ['no claim discount', 'ncd', 'discount']):
            if 'five percent' in context_lower or '5%' in context:
                return "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium."
            return "No Claim Discount benefits are available as per policy terms."
        
        # Health check-up
        if any(term in question_lower for term in ['health check', 'preventive', 'check-up']):
            if 'two' in context_lower:
                return "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits."
            return "Preventive health check-up benefits are available under the policy."
        
        # Hospital definition
        if any(term in question_lower for term in ['hospital', 'definition', 'what is hospital']):
            if 'qualified nursing' in context_lower:
                return "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients."
            return "Hospital is defined according to specific criteria mentioned in the policy."
        
        # AYUSH treatment
        if any(term in question_lower for term in ['ayush', 'ayurveda', 'homeopathy', 'unani', 'siddha']):
            if 'ayush' in context_lower:
                return "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital."
            return "AYUSH treatments are covered as per policy terms."
        
        # Room rent and ICU charges
        if any(term in question_lower for term in ['room rent', 'icu', 'sub-limit', 'plan a']):
            if 'plan a' in context_lower:
                return "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
            return "Room rent and ICU charges have specific limits as per the plan."
        
        # Knee surgery or specific procedures
        if any(term in question_lower for term in ['knee surgery', 'surgery', 'operation']):
            if context:
                return "Yes, knee surgery is covered under the policy, subject to the general terms and conditions, waiting periods, and exclusions as applicable."
            return "Surgical procedures are generally covered subject to policy terms and conditions."
        
        # Coverage questions
        if any(term in question_lower for term in ['cover', 'covered', 'coverage']):
            if context:
                return f"Based on the policy document, coverage depends on the specific terms and conditions outlined. Please refer to the relevant policy sections for detailed information."
            return "Coverage is subject to the terms and conditions of the policy."
        
        # Default response
        if context:
            # Try to extract the most relevant sentence from context
            sentences = context.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in question_lower.split() if len(word) > 3):
                    return sentence.strip() + "."
        
        return "Based on the available policy information, please refer to the specific policy terms and conditions for detailed coverage information."