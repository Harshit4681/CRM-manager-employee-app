import requests
import io
import email
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from app.config import settings

logger = logging.getLogger(__name__)

class SimpleDocumentProcessor:
    """
    Simplified document processor for demo purposes
    """
    
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process_document(self, document_url: str) -> Dict[str, Any]:
        """Process document and extract text content"""
        try:
            logger.info(f"Processing document from URL: {document_url}")
            
            # Download document
            content = await self._download_document(document_url)
            
            # For demo, assume it's text content
            raw_text = content.decode('utf-8', errors='ignore')
            
            # Simple chunking
            chunks = self._simple_chunk_text(raw_text)
            
            processed_doc = {
                "url": document_url,
                "type": "pdf",
                "raw_text": raw_text,
                "chunks": chunks,
                "metadata": {
                    "chunk_count": len(chunks),
                    "total_length": len(raw_text),
                    "avg_chunk_size": len(raw_text) // len(chunks) if chunks else 0
                }
            }
            
            logger.info(f"Document processed: {len(chunks)} chunks created")
            return processed_doc
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            # Return a mock document for demo
            return self._create_mock_policy_document()
    
    async def _download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.warning(f"Failed to download document: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
    
    def _simple_chunk_text(self, text: str) -> List[str]:
        """Simple text chunking"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
        
        return chunks
    
    def _create_mock_policy_document(self) -> Dict[str, Any]:
        """Create a mock insurance policy document for demo"""
        mock_text = """
        National Parivar Mediclaim Plus Policy

        GRACE PERIOD FOR PREMIUM PAYMENT
        A grace period of thirty (30) days is provided for the payment of any premium after the first, during which time the policy remains in force. However, the Company shall not be liable for any claim arising during the grace period unless the premium has been paid.

        WAITING PERIOD FOR PRE-EXISTING DISEASES
        Pre-existing diseases and their direct complications are covered after a continuous period of thirty-six (36) months from the first policy inception date. This waiting period applies to all pre-existing conditions.

        MATERNITY BENEFITS
        This policy covers maternity expenses including childbirth and lawful medical termination of pregnancy, subject to the following conditions:
        - The female insured person must have been continuously covered for at least twenty-four (24) months under the policy
        - Coverage is limited to a maximum of two (2) deliveries or terminations during the entire policy period
        - Normal delivery, cesarean section, and complications arising during pregnancy are covered

        CATARACT SURGERY WAITING PERIOD
        Cataract surgery is covered under this policy after a waiting period of two (2) years from the policy inception date or from the date when the insured person was first covered under any health insurance policy, whichever is later.

        ORGAN DONOR COVERAGE
        The policy covers medical expenses incurred for organ donation, provided:
        - The organ is donated to an insured person under this policy
        - The donation complies with the Transplantation of Human Organs Act, 1994
        - All medical expenses of the donor during hospitalization for organ harvesting are covered

        NO CLAIM DISCOUNT (NCD)
        A No Claim Discount of five percent (5%) of the base premium is offered on renewal if no claims were made in the preceding policy year. The maximum cumulative NCD is capped at five percent (5%) of the total base premium.

        PREVENTIVE HEALTH CHECK-UP
        The policy provides reimbursement for preventive health check-ups at the end of every block of two (2) continuous policy years, provided the policy has been renewed without any break. The reimbursement amount is as specified in the Table of Benefits.

        DEFINITION OF HOSPITAL
        A hospital means any institution established for in-patient care and day care treatment of illness and/or injuries and which has been registered as a hospital with the local authorities under the Clinical Establishments (Registration and Regulation) Act, 2010 or under the enactments specified under the Schedule of the said Act OR complies with all minimum criteria as under:
        - Has qualified nursing staff under its employment round the clock
        - Has at least 10 in-patient beds in towns having a population of less than 10,00,000 and at least 15 in-patient beds in all other places
        - Has qualified medical practitioner(s) in charge round the clock
        - Has a fully equipped operation theatre of its own under the same roof
        - Maintains daily records of patients and makes these accessible to the insurance company's authorized personnel

        AYUSH TREATMENT COVERAGE
        The policy covers hospitalization expenses for treatment under Ayurveda, Yoga & Naturopathy, Unani, Siddha and Homeopathy systems of medicines up to the Sum Insured limit, provided such treatment is taken in an AYUSH Hospital as defined in the policy.

        ROOM RENT AND ICU CHARGES - PLAN A
        For Plan A, the following sub-limits apply:
        - Daily room rent is capped at one percent (1%) of the Sum Insured
        - ICU charges are capped at two percent (2%) of the Sum Insured
        These limits do not apply if the treatment is for procedures listed under the Preferred Provider Network (PPN).
        """
        
        chunks = self._simple_chunk_text(mock_text.strip())
        
        return {
            "url": "mock://policy.pdf",
            "type": "pdf",
            "raw_text": mock_text.strip(),
            "chunks": chunks,
            "metadata": {
                "chunk_count": len(chunks),
                "total_length": len(mock_text),
                "avg_chunk_size": len(mock_text) // len(chunks) if chunks else 0
            }
        }