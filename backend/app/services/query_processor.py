import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.models.schemas import ParsedQuery, QueryIntent
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Service for parsing and understanding natural language queries"""
    
    def __init__(self):
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
        
    def _build_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Build patterns for intent classification"""
        return {
            QueryIntent.POLICY_SEARCH: [
                r'find.*policy', r'search.*policy', r'show.*policy',
                r'policy.*details', r'policy.*information', r'policy.*terms',
                r'coverage.*details', r'insurance.*policy'
            ],
            QueryIntent.CLAIM_VALIDATION: [
                r'claim.*valid', r'eligible.*claim', r'claim.*approval',
                r'submit.*claim', r'claim.*process', r'claim.*status',
                r'can.*claim', r'covered.*claim'
            ],
            QueryIntent.COVERAGE_CHECK: [
                r'covered.*under', r'coverage.*for', r'what.*covered',
                r'does.*cover', r'is.*covered', r'coverage.*include',
                r'benefits.*include', r'plan.*cover'
            ],
            QueryIntent.PREMIUM_CALCULATION: [
                r'premium.*cost', r'how.*much.*premium', r'cost.*policy',
                r'price.*policy', r'premium.*calculation', r'monthly.*cost',
                r'annual.*premium', r'premium.*amount'
            ],
            QueryIntent.DOCUMENT_ANALYSIS: [
                r'analyze.*document', r'review.*document', r'summarize.*document',
                r'extract.*information', r'key.*points', r'document.*summary'
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for entity extraction"""
        return {
            'age': [
                r'(\d{1,3})\s*(?:years?\s*old|yr|y\.o\.)',
                r'age\s*(?:of\s*)?(\d{1,3})',
                r'(\d{1,3})\s*(?:M|F|Male|Female)'
            ],
            'medical_condition': [
                r'(?:knee|hip|shoulder|back|spine|heart|diabetes|cancer|surgery)',
                r'(?:hypertension|blood pressure|cholesterol)',
                r'(?:arthritis|fracture|injury|accident)',
                r'(?:chronic|acute|medical condition)'
            ],
            'location': [
                r'(?:Mumbai|Delhi|Bangalore|Pune|Chennai|Kolkata|Hyderabad)',
                r'(?:India|Indian)',
                r'(?:city|state|region|area)'
            ],
            'time_period': [
                r'(\d+)\s*(?:month|year|day|week)s?',
                r'(?:last|past|next|within)\s*(\d+)',
                r'(\d+)\s*(?:M|Y|D|W)'
            ],
            'policy_type': [
                r'(?:health|medical|life|auto|home|travel)\s*(?:insurance|policy)',
                r'(?:term|whole|universal)\s*life',
                r'(?:comprehensive|third party)\s*auto'
            ],
            'amount': [
                r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
                r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees?|INR|Rs\.?)',
                r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakhs?|crores?)'
            ]
        }
    
    async def parse_query(self, query: str) -> ParsedQuery:
        """
        Parse natural language query and extract intent and entities
        
        Args:
            query: Natural language query string
            
        Returns:
            ParsedQuery with intent, entities, keywords, and filters
        """
        try:
            logger.info(f"Parsing query: {query[:100]}...")
            
            # Normalize query
            normalized_query = self._normalize_query(query)
            
            # Classify intent
            intent = self._classify_intent(normalized_query)
            
            # Extract entities
            entities = self._extract_entities(normalized_query)
            
            # Extract keywords
            keywords = self._extract_keywords(normalized_query)
            
            # Build filters based on entities
            filters = self._build_filters(entities)
            
            parsed_query = ParsedQuery(
                intent=intent,
                entities=entities,
                keywords=keywords,
                filters=filters
            )
            
            logger.info(f"Parsed query - Intent: {intent}, Entities: {len(entities)}")
            return parsed_query
            
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            # Return default parsing
            return ParsedQuery(
                intent=QueryIntent.GENERAL_QUERY,
                entities={},
                keywords=query.split()[:10],  # Simple fallback
                filters={}
            )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query text"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Handle common abbreviations
        abbreviations = {
            'yrs': 'years',
            'yr': 'year',
            'y.o.': 'years old',
            'm': 'male',
            'f': 'female',
            'w/': 'with',
            'w/o': 'without',
            'hx': 'history',
            'dx': 'diagnosis',
            'rx': 'prescription'
        }
        
        for abbr, full in abbreviations.items():
            query = re.sub(r'\b' + re.escape(abbr) + r'\b', full, query)
        
        return query
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify query intent using pattern matching"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            # Return intent with highest score
            return max(intent_scores, key=intent_scores.get)
        
        # Default intent
        return QueryIntent.GENERAL_QUERY
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            entity_values = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    if match.groups():
                        # Extract captured groups
                        for group in match.groups():
                            if group and group.strip():
                                entity_values.append(group.strip())
                    else:
                        # Extract full match
                        entity_values.append(match.group().strip())
            
            if entity_values:
                entities[entity_type] = list(set(entity_values))  # Remove duplicates
        
        # Post-process specific entity types
        entities = self._post_process_entities(entities, query)
        
        return entities
    
    def _post_process_entities(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Post-process extracted entities for better accuracy"""
        
        # Process age entities
        if 'age' in entities:
            ages = []
            for age_str in entities['age']:
                try:
                    age = int(re.findall(r'\d+', age_str)[0])
                    if 0 <= age <= 150:  # Reasonable age range
                        ages.append(age)
                except (ValueError, IndexError):
                    pass
            entities['age'] = ages if ages else None
        
        # Process amounts
        if 'amount' in entities:
            amounts = []
            for amount_str in entities['amount']:
                try:
                    # Remove commas and extract numeric value
                    amount = float(re.sub(r'[,₹Rs\.]', '', amount_str))
                    amounts.append(amount)
                except ValueError:
                    pass
            entities['amount'] = amounts if amounts else None
        
        # Process time periods
        if 'time_period' in entities:
            periods = []
            for period_str in entities['time_period']:
                period_match = re.search(r'(\d+)\s*(month|year|day|week)', period_str)
                if period_match:
                    periods.append({
                        'value': int(period_match.group(1)),
                        'unit': period_match.group(2)
                    })
            entities['time_period'] = periods if periods else None
        
        # Extract gender from context
        gender_patterns = [
            (r'\b(?:male|man|boy|he|his|him)\b', 'male'),
            (r'\b(?:female|woman|girl|she|her)\b', 'female')
        ]
        
        for pattern, gender in gender_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                entities['gender'] = gender
                break
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        # Remove stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'i', 'me', 'my', 'we', 'us',
            'you', 'your', 'this', 'that', 'these', 'those', 'can', 'could',
            'should', 'would', 'have', 'had', 'do', 'does', 'did', 'am'
        }
        
        # Split into words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:20]  # Limit to top 20 keywords
    
    def _build_filters(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Build search filters based on extracted entities"""
        filters = {}
        
        # Age-based filters
        if 'age' in entities and entities['age']:
            ages = entities['age']
            if isinstance(ages, list) and ages:
                age = ages[0]  # Use first age found
                # Create age ranges for better matching
                if age < 25:
                    filters['age_group'] = 'young'
                elif age < 65:
                    filters['age_group'] = 'adult'
                else:
                    filters['age_group'] = 'senior'
                
                filters['age'] = age
        
        # Location-based filters
        if 'location' in entities and entities['location']:
            filters['location'] = entities['location'][0].lower()
        
        # Policy type filters
        if 'policy_type' in entities and entities['policy_type']:
            filters['policy_type'] = entities['policy_type'][0].lower()
        
        # Medical condition filters
        if 'medical_condition' in entities and entities['medical_condition']:
            filters['medical_conditions'] = [
                condition.lower() for condition in entities['medical_condition']
            ]
        
        # Time period filters
        if 'time_period' in entities and entities['time_period']:
            periods = entities['time_period']
            if isinstance(periods, list) and periods:
                period = periods[0]
                if isinstance(period, dict):
                    filters['time_period'] = period
        
        # Amount filters
        if 'amount' in entities and entities['amount']:
            amounts = entities['amount']
            if isinstance(amounts, list) and amounts:
                filters['amount'] = amounts[0]
        
        # Gender filters
        if 'gender' in entities:
            filters['gender'] = entities['gender']
        
        return filters
    
    def get_query_complexity(self, parsed_query: ParsedQuery) -> str:
        """Assess query complexity for processing optimization"""
        complexity_score = 0
        
        # Intent complexity
        complex_intents = [
            QueryIntent.CLAIM_VALIDATION,
            QueryIntent.PREMIUM_CALCULATION,
            QueryIntent.DOCUMENT_ANALYSIS
        ]
        if parsed_query.intent in complex_intents:
            complexity_score += 2
        
        # Entity complexity
        entity_count = len(parsed_query.entities)
        if entity_count > 3:
            complexity_score += 2
        elif entity_count > 1:
            complexity_score += 1
        
        # Keyword complexity
        if len(parsed_query.keywords) > 10:
            complexity_score += 1
        
        # Filter complexity
        if len(parsed_query.filters) > 2:
            complexity_score += 1
        
        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "moderate"
        else:
            return "simple"
    
    def suggest_refinements(self, parsed_query: ParsedQuery) -> List[str]:
        """Suggest query refinements for better results"""
        suggestions = []
        
        # Missing entity suggestions
        if not parsed_query.entities.get('age'):
            suggestions.append("Consider specifying age for more accurate results")
        
        if not parsed_query.entities.get('location'):
            suggestions.append("Adding location information may improve relevance")
        
        if parsed_query.intent == QueryIntent.GENERAL_QUERY:
            suggestions.append("Try to be more specific about what you're looking for")
        
        # Intent-specific suggestions
        if parsed_query.intent == QueryIntent.CLAIM_VALIDATION:
            if not parsed_query.entities.get('medical_condition'):
                suggestions.append("Specify the medical condition for claim validation")
        
        if parsed_query.intent == QueryIntent.PREMIUM_CALCULATION:
            missing_factors = []
            if not parsed_query.entities.get('age'):
                missing_factors.append("age")
            if not parsed_query.entities.get('location'):
                missing_factors.append("location")
            
            if missing_factors:
                suggestions.append(f"For premium calculation, consider adding: {', '.join(missing_factors)}")
        
        return suggestions