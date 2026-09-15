"""
OCR Service for Prescription Text Extraction
Handles image preprocessing, OCR processing, and text parsing for prescription images.
"""

import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Data class for OCR results"""
    raw_text: str
    confidence_score: float
    structured_data: Dict
    preprocessing_applied: List[str]
    ocr_engine: str

class PrescriptionOCR:
    """Main OCR class for prescription processing"""
    
    def __init__(self):
        """Initialize OCR engines and configuration"""
        self.easyocr_reader = easyocr.Reader(['en'])
        
        # Configure Tesseract path if on Windows
        if os.name == 'nt':  # Windows
            # Common Tesseract installation paths
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', ''))
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
            else:
                logger.warning("Tesseract executable not found. Please install Tesseract OCR.")
        
        # OCR configuration
        self.tesseract_config = '--psm 6 -l eng'
        
        # Prescription keywords for validation
        self.prescription_keywords = [
            'prescription', 'rx', 'medication', 'medicine', 'drug', 'tablet', 'capsule',
            'mg', 'ml', 'dose', 'dosage', 'daily', 'twice', 'times', 'per', 'day',
            'morning', 'evening', 'night', 'before', 'after', 'meal', 'food',
            'doctor', 'dr', 'physician', 'patient', 'take', 'use', 'apply'
        ]

    def preprocess_image(self, image_path: str) -> Tuple[np.ndarray, List[str]]:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of processed image array and list of applied preprocessing steps
        """
        applied_steps = []
        
        try:
            # Load image
            if image_path.lower().endswith('.pdf'):
                # Convert PDF to image
                images = convert_from_path(image_path, first_page=1, last_page=1)
                image = np.array(images[0])
                applied_steps.append("PDF to image conversion")
            else:
                image = cv2.imread(image_path)
                applied_steps.append("Image loaded")
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            applied_steps.append("Grayscale conversion")
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            applied_steps.append("Noise reduction")
            
            # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            applied_steps.append("Contrast enhancement")
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (1, 1), 0)
            applied_steps.append("Gaussian blur")
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
            applied_steps.append("Morphological operations")
            
            return morph, applied_steps
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            # Return original image if preprocessing fails
            try:
                original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                return original, ["Original image (preprocessing failed)"]
            except:
                raise ValueError(f"Failed to load image: {image_path}")

    def extract_text_tesseract(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Preprocessed image array
            
        Returns:
            Tuple of extracted text and confidence score
        """
        try:
            # Check if Tesseract is available
            if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not pytesseract.pytesseract.tesseract_cmd:
                logger.warning("Tesseract not configured, skipping Tesseract OCR")
                return "", 0.0
                
            # Get text with confidence data
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
            
            return text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {str(e)}")
            return "", 0.0

    def extract_text_easyocr(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extract text using EasyOCR
        
        Args:
            image: Preprocessed image array
            
        Returns:
            Tuple of extracted text and confidence score
        """
        try:
            # Use EasyOCR to extract text
            results = self.easyocr_reader.readtext(image, detail=1)
            
            # Combine text and calculate average confidence
            text_parts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                if conf > 0.3:  # Filter out low-confidence results
                    text_parts.append(text)
                    confidences.append(conf)
            
            combined_text = ' '.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return combined_text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"EasyOCR error: {str(e)}")
            return "", 0.0

    def parse_prescription_text(self, text: str) -> Dict:
        """
        Parse prescription text to extract structured data
        
        Args:
            text: Raw OCR text
            
        Returns:
            Dictionary with structured prescription data
        """
        structured_data = {
            'medication_name': '',
            'dosage': '',
            'frequency': '',
            'duration': '',
            'doctor_name': '',
            'patient_name': '',
            'date': '',
            'instructions': ''
        }
        
        # Clean and normalize text
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        cleaned_lower = cleaned_text.lower()
        
        try:
            # Extract medication name (improved patterns)
            med_patterns = [
                # Look for drug names with common suffixes
                r'\b([A-Z][a-z]+(?:cillin|mycin|pril|olol|ide|ine|mab|nib|stat|prazole|floxacin|cycline))\b',
                # Look for capitalized drug names near dosage
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+\d+\s*(?:mg|ml|g|mcg)',
                # Look after medication/medicine keywords
                r'(?:medication|medicine|drug)[:.\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                # Look for standalone capitalized words that might be drugs
                r'\b([A-Z][a-z]{4,}(?:\s+[A-Z][a-z]+)?)(?=\s+\d+(?:mg|ml|g))',
            ]
            
            for pattern in med_patterns:
                matches = re.findall(pattern, cleaned_text)
                if matches:
                    # Filter out common non-drug words
                    non_drugs = {'prescription', 'patient', 'doctor', 'take', 'times', 'daily', 'for', 'days'}
                    for match in matches:
                        if match.lower() not in non_drugs and len(match) > 3:
                            structured_data['medication_name'] = match.strip()
                            break
                    if structured_data['medication_name']:
                        break
            
            # Extract dosage (look for mg, ml, g patterns)
            dosage_patterns = [
                r'(\d+(?:\.\d+)?\s*(?:mg|ml|g|mcg|units?))',
                r'(\d+(?:\.\d+)?\s*milligrams?)',
                r'(\d+(?:\.\d+)?\s*grams?)'
            ]
            
            for pattern in dosage_patterns:
                match = re.search(pattern, cleaned_lower)
                if match:
                    structured_data['dosage'] = match.group(1).strip()
                    break
            
            # Extract frequency (improved patterns)
            frequency_patterns = [
                # Handle "3 times daily" variations (including OCR errors)
                r'(\d+\s*times?\s*(?:per\s*)?day|\d+\s*times?\s*daily)',
                r'(\d+\s*timesdaily)',  # OCR error: "timesdaily"
                r'(\d+x\s*daily|\d+\s*x\s*day)',
                # Standard frequency terms
                r'(once\s*(?:a\s*)?daily|twice\s*(?:a\s*)?daily|three\s*times\s*(?:a\s*)?daily)',
                r'(every\s*\d+\s*hours?)',
                r'(morning|evening|night)',
                r'(bid|tid|qid|qd|od)',  # Medical abbreviations
                # Handle "Take 3 times daily" pattern
                r'take\s*(\d+\s*times?\s*daily)',
                # Just "daily" on its own
                r'\b(daily)\b'
            ]
            
            for pattern in frequency_patterns:
                match = re.search(pattern, cleaned_lower)
                if match:
                    freq = match.group(1).strip()
                    # Fix OCR errors
                    if 'timesdaily' in freq:
                        freq = re.sub(r'(\d+)\s*timesdaily', r'\1 times daily', freq)
                    structured_data['frequency'] = freq
                    break
            
            # Extract duration
            duration_patterns = [
                r'for\s*(\d+\s*(?:days?|weeks?|months?))',
                r'\b(\d+\s*(?:days?|weeks?|months?))\b',
                r'(until\s+finished)',
                r'(\d+\s*day\s*course)'
            ]
            
            for pattern in duration_patterns:
                match = re.search(pattern, cleaned_lower)
                if match:
                    structured_data['duration'] = match.group(1).strip()
                    break
            
            # Extract doctor name (improved)
            doctor_patterns = [
                r'(?:dr\.?|doctor)\s*[:.\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'physician[:.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'\bDr\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            
            for pattern in doctor_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    doctor_name = match.group(1).strip()
                    # Filter out medication names that might be misidentified
                    if doctor_name != structured_data['medication_name']:
                        structured_data['doctor_name'] = doctor_name
                        break
            
            # Extract patient name
            patient_patterns = [
                r'(?:patient|pt)[:.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'name[:.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'for[:.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            
            for pattern in patient_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    patient_name = match.group(1).strip()
                    # Filter out doctor and medication names
                    if (patient_name != structured_data['doctor_name'] and 
                        patient_name != structured_data['medication_name']):
                        structured_data['patient_name'] = patient_name
                        break
            
            # Extract date
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
                r'(\d{4}-\d{1,2}-\d{1,2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, cleaned_lower)
                if match:
                    structured_data['date'] = match.group(1).strip()
                    break
            
            # Extract special instructions
            instruction_patterns = [
                r'(take\s+with\s+food)',
                r'(take\s+before\s+meals?)',
                r'(take\s+after\s+meals?)',
                r'(on\s+empty\s+stomach)',
                r'(with\s+water)',
                r'(as\s+needed)',
                r'(do\s+not\s+exceed)',
                r'(avoid\s+alcohol)',
                r'(with\s+meals?)'
            ]
            
            instructions = []
            for pattern in instruction_patterns:
                matches = re.findall(pattern, cleaned_lower)
                instructions.extend(matches)
            
            structured_data['instructions'] = '; '.join(instructions) if instructions else ''
            
        except Exception as e:
            logger.error(f"Error parsing prescription text: {str(e)}")
        
        return structured_data

    def validate_prescription(self, text: str, structured_data: Dict) -> bool:
        """
        Validate if the extracted text appears to be a prescription
        
        Args:
            text: Raw OCR text
            structured_data: Parsed structured data
            
        Returns:
            Boolean indicating if this appears to be a valid prescription
        """
        # Check for prescription keywords
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in self.prescription_keywords if keyword in text_lower)
        
        # Check if we extracted key prescription components
        has_medication = bool(structured_data.get('medication_name'))
        has_dosage = bool(structured_data.get('dosage'))
        has_frequency = bool(structured_data.get('frequency'))
        
        # Validation criteria
        has_keywords = keyword_count >= 3
        has_structure = sum([has_medication, has_dosage, has_frequency]) >= 2
        
        return has_keywords or has_structure

    async def process_prescription(self, image_path: str) -> OCRResult:
        """
        Main method to process prescription image/PDF
        
        Args:
            image_path: Path to the prescription image or PDF
            
        Returns:
            OCRResult object with extracted and parsed data
        """
        try:
            # Preprocess image
            processed_image, preprocessing_steps = self.preprocess_image(image_path)
            
            # Try both OCR engines and use the best result
            tesseract_text, tesseract_conf = self.extract_text_tesseract(processed_image)
            easyocr_text, easyocr_conf = self.extract_text_easyocr(processed_image)
            
            # Choose the best OCR result based on confidence and text length
            if tesseract_conf > 0 and tesseract_conf > easyocr_conf and len(tesseract_text) > len(easyocr_text) * 0.8:
                best_text = tesseract_text
                best_conf = tesseract_conf
                best_engine = "Tesseract"
            else:
                best_text = easyocr_text
                best_conf = easyocr_conf
                best_engine = "EasyOCR"
            
            # If both results are poor and both engines worked, combine them
            if best_conf < 0.5 and tesseract_conf > 0:
                combined_text = f"{tesseract_text}\n{easyocr_text}"
                best_text = combined_text
                best_conf = max(tesseract_conf, easyocr_conf)
                best_engine = "Combined"
            elif not best_text:  # If EasyOCR also failed
                logger.error("Both OCR engines failed to extract text")
                best_text = ""
                best_conf = 0.0
                best_engine = "None"
            
            # Parse structured data
            structured_data = self.parse_prescription_text(best_text)
            
            # Validate prescription
            is_valid = self.validate_prescription(best_text, structured_data)
            if not is_valid:
                logger.warning("Extracted text does not appear to be a valid prescription")
                best_conf *= 0.5  # Reduce confidence for invalid prescriptions
            
            return OCRResult(
                raw_text=best_text,
                confidence_score=best_conf,
                structured_data=structured_data,
                preprocessing_applied=preprocessing_steps,
                ocr_engine=best_engine
            )
            
        except Exception as e:
            logger.error(f"Error processing prescription {image_path}: {str(e)}")
            return OCRResult(
                raw_text="",
                confidence_score=0.0,
                structured_data={},
                preprocessing_applied=["Error occurred"],
                ocr_engine="None"
            )

# Global OCR instance
ocr_processor = PrescriptionOCR()

async def process_prescription_ocr(image_path: str) -> Dict:
    """
    Convenience function for processing prescription images
    
    Args:
        image_path: Path to prescription image or PDF
        
    Returns:
        Dictionary with OCR results compatible with existing API
    """
    result = await ocr_processor.process_prescription(image_path)
    
    return {
        "extracted_text": result.raw_text,
        "confidence_score": result.confidence_score,
        "structured_data": result.structured_data,
        "preprocessing_applied": result.preprocessing_applied,
        "ocr_engine": result.ocr_engine
    }