"""
NLP module for parsing prescription text and extracting structured medication data.
"""

import re
import os
import httpx
from typing import Dict, List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from loguru import logger

class PrescriptionParser:
    """NLP parser for extracting structured data from prescription text."""
    
    def __init__(self):
        """Initialize NLP models and patterns."""
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.hf_model_url = os.getenv("HUGGINGFACE_MODEL_URL", "https://api-inference.huggingface.co/models/")
        
        # Regex patterns for medication extraction
        self.medication_patterns = {
            'medication_name': [
                r'\\b([A-Z][a-z]+(?:in|ol|ide|ine|ate|ium)?(?:\\s+[A-Z][a-z]+)?)\\b',
                r'\\b([A-Z]{2,}(?:\\s+[A-Z]{2,})?)\\b'
            ],
            'dosage': [
                r'(\\d+(?:\\.\\d+)?\\s*(?:mg|ml|g|mcg|units?))\\b',
                r'(\\d+(?:\\.\\d+)?\\s*(?:milligrams?|milliliters?|grams?|micrograms?))\\b'
            ],
            'frequency': [
                r'(\\d+\\s*times?\\s*(?:daily|per day|a day))\\b',
                r'(once|twice|thrice)\\s*(?:daily|per day|a day)\\b',
                r'(every\\s+\\d+\\s*hours?)\\b',
                r'(morning|evening|night|bedtime)\\b',
                r'(before|after)\\s*meals?\\b'
            ],
            'duration': [
                r'(for\\s+\\d+\\s*(?:days?|weeks?|months?))\\b',
                r'(\\d+\\s*(?:days?|weeks?|months?))\\b'
            ]
        }
        
        # Load pre-trained NER model for medical entities
        try:
            # Use a pre-trained biomedical NER model if available
            self.ner_pipeline = None
            # self.ner_pipeline = pipeline("ner", model="d4data/biomedical-ner-all")
        except Exception as e:
            logger.warning(f"Could not load NER model: {str(e)}")
            self.ner_pipeline = None
    
    def extract_with_regex(self, text: str) -> Dict:
        """Extract medication data using regex patterns."""
        extracted_data = {
            'medication_name': [],
            'dosage': [],
            'frequency': [],
            'duration': []
        }
        
        try:
            for field, patterns in self.medication_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        # Clean and deduplicate matches
                        cleaned_matches = list(set([match.strip() for match in matches if match.strip()]))
                        extracted_data[field].extend(cleaned_matches)
            
            # Remove duplicates
            for field in extracted_data:
                extracted_data[field] = list(set(extracted_data[field]))
            
            return extracted_data
        
        except Exception as e:
            logger.error(f"Regex extraction error: {str(e)}")
            return extracted_data
    
    async def extract_with_huggingface(self, text: str) -> Dict:
        """Extract entities using Hugging Face API."""
        try:
            if not self.hf_api_key:
                return {}
            
            # Use Hugging Face Inference API
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            api_url = f"{self.hf_model_url}emilyalsentzer/Bio_ClinicalBERT"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={"inputs": text}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._process_hf_result(result)
                else:
                    logger.warning(f"Hugging Face API error: {response.status_code}")
                    return {}
        
        except Exception as e:
            logger.error(f"Hugging Face extraction error: {str(e)}")
            return {}
    
    def _process_hf_result(self, result: List) -> Dict:
        """Process Hugging Face NER results."""
        processed = {
            'medication_name': [],
            'dosage': [],
            'frequency': [],
            'duration': []
        }
        
        try:
            for entity in result:
                entity_text = entity.get('word', '').strip()
                entity_label = entity.get('entity', '').upper()
                
                # Map entity labels to our categories
                if 'DRUG' in entity_label or 'MEDICATION' in entity_label:
                    processed['medication_name'].append(entity_text)
                elif 'DOSAGE' in entity_label or 'STRENGTH' in entity_label:
                    processed['dosage'].append(entity_text)
                elif 'FREQUENCY' in entity_label:
                    processed['frequency'].append(entity_text)
                elif 'DURATION' in entity_label:
                    processed['duration'].append(entity_text)
            
            return processed
        
        except Exception as e:
            logger.error(f"HF result processing error: {str(e)}")
            return processed
    
    def normalize_medication_name(self, medication: str) -> str:
        """Normalize medication name for consistency."""
        try:
            # Remove common prefixes/suffixes
            medication = medication.strip()
            medication = re.sub(r'^(generic|brand)\\s+', '', medication, flags=re.IGNORECASE)
            
            # Capitalize first letter of each word
            medication = ' '.join(word.capitalize() for word in medication.split())
            
            return medication
        
        except Exception as e:
            logger.error(f"Medication normalization error: {str(e)}")
            return medication
    
    def normalize_dosage(self, dosage: str) -> str:
        """Normalize dosage format."""
        try:
            # Standardize units
            dosage = re.sub(r'\\bmilligrams?\\b', 'mg', dosage, flags=re.IGNORECASE)
            dosage = re.sub(r'\\bmilliliters?\\b', 'ml', dosage, flags=re.IGNORECASE)
            dosage = re.sub(r'\\bgrams?\\b', 'g', dosage, flags=re.IGNORECASE)
            dosage = re.sub(r'\\bmicrograms?\\b', 'mcg', dosage, flags=re.IGNORECASE)
            
            # Remove extra spaces
            dosage = re.sub(r'\\s+', ' ', dosage).strip()
            
            return dosage
        
        except Exception as e:
            logger.error(f"Dosage normalization error: {str(e)}")
            return dosage
    
    def normalize_frequency(self, frequency: str) -> str:
        """Normalize frequency format."""
        try:
            # Standardize common frequencies
            frequency_map = {
                'once daily': '1x daily',
                'twice daily': '2x daily', 
                'thrice daily': '3x daily',
                'once a day': '1x daily',
                'twice a day': '2x daily',
                'three times a day': '3x daily',
                'four times a day': '4x daily'
            }
            
            frequency_lower = frequency.lower()
            for pattern, replacement in frequency_map.items():
                frequency_lower = frequency_lower.replace(pattern, replacement)
            
            return frequency_lower
        
        except Exception as e:
            logger.error(f"Frequency normalization error: {str(e)}")
            return frequency
    
    async def parse_prescription(self, text: str) -> Dict:
        """Parse prescription text and extract structured data."""
        try:
            # Extract using regex patterns
            regex_results = self.extract_with_regex(text)
            
            # Extract using Hugging Face if available
            hf_results = await self.extract_with_huggingface(text)
            
            # Combine results
            combined_results = {}
            for field in ['medication_name', 'dosage', 'frequency', 'duration']:
                combined_list = []
                
                # Add regex results
                if regex_results.get(field):
                    combined_list.extend(regex_results[field])
                
                # Add Hugging Face results
                if hf_results.get(field):
                    combined_list.extend(hf_results[field])
                
                # Remove duplicates and normalize
                unique_items = list(set(combined_list))
                
                if field == 'medication_name':
                    unique_items = [self.normalize_medication_name(item) for item in unique_items]
                elif field == 'dosage':
                    unique_items = [self.normalize_dosage(item) for item in unique_items]
                elif field == 'frequency':
                    unique_items = [self.normalize_frequency(item) for item in unique_items]
                
                combined_results[field] = unique_items
            
            # Structure the final result
            structured_data = {
                'medications': [],
                'raw_extractions': combined_results,
                'confidence': self._calculate_confidence(combined_results)
            }
            
            # Try to create medication objects
            medications = self._create_medication_objects(combined_results)
            structured_data['medications'] = medications
            
            return structured_data
        
        except Exception as e:
            logger.error(f"Prescription parsing error: {str(e)}")
            return {
                'medications': [],
                'raw_extractions': {},
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _create_medication_objects(self, extractions: Dict) -> List[Dict]:
        """Create structured medication objects from extractions."""
        medications = []
        
        try:
            med_names = extractions.get('medication_name', [])
            dosages = extractions.get('dosage', [])
            frequencies = extractions.get('frequency', [])
            durations = extractions.get('duration', [])
            
            # Simple approach: pair first items together
            max_items = max(len(med_names), len(dosages), len(frequencies))
            
            for i in range(max_items):
                medication = {
                    'name': med_names[i] if i < len(med_names) else '',
                    'dosage': dosages[i] if i < len(dosages) else '',
                    'frequency': frequencies[i] if i < len(frequencies) else '',
                    'duration': durations[i] if i < len(durations) else ''
                }
                
                # Only add if we have at least name and dosage
                if medication['name'] and medication['dosage']:
                    medications.append(medication)
            
            return medications
        
        except Exception as e:
            logger.error(f"Medication object creation error: {str(e)}")
            return []
    
    def _calculate_confidence(self, extractions: Dict) -> float:
        """Calculate confidence score based on extraction completeness."""
        try:
            total_fields = 4  # medication_name, dosage, frequency, duration
            filled_fields = sum(1 for field_data in extractions.values() if field_data)
            
            base_confidence = filled_fields / total_fields
            
            # Bonus for having medication name and dosage (most important)
            if extractions.get('medication_name') and extractions.get('dosage'):
                base_confidence += 0.2
            
            return min(base_confidence, 1.0)
        
        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.0

async def parse_prescription_text(text: str) -> Dict:
    """Parse prescription text and return structured data."""
    try:
        parser = PrescriptionParser()
        result = await parser.parse_prescription(text)
        
        logger.info("Prescription text parsing completed")
        return result
    
    except Exception as e:
        logger.error(f"Prescription text parsing error: {str(e)}")
        return {
            'medications': [],
            'raw_extractions': {},
            'confidence': 0.0,
            'error': str(e)
        }