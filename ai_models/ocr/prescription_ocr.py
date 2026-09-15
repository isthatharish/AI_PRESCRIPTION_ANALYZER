"""
OCR module for prescription text extraction using Tesseract and EasyOCR.
"""

import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
import os
from typing import Dict, List, Tuple
import re
from loguru import logger

class PrescriptionOCR:
    """OCR processor for prescription documents."""
    
    def __init__(self):
        """Initialize OCR processors."""
        self.tesseract_cmd = os.getenv("TESSERACT_CMD_PATH", "tesseract")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        self.easyocr_reader = easyocr.Reader(['en'])
        self.confidence_threshold = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.7"))
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Read image
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
            
            return closing
        
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    def extract_with_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract OCR."""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Configure Tesseract
            config = '--oem 3 --psm 6 -l eng'
            
            # Extract text with confidence
            data = pytesseract.image_to_data(
                processed_image, 
                config=config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Filter by confidence
            text_blocks = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > self.confidence_threshold * 100:
                    text = data['text'][i].strip()
                    if text:
                        text_blocks.append(text)
                        confidences.append(int(data['conf'][i]) / 100.0)
            
            extracted_text = ' '.join(text_blocks)
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                'text': extracted_text,
                'confidence': avg_confidence,
                'method': 'tesseract'
            }
        
        except Exception as e:
            logger.error(f"Tesseract extraction error: {str(e)}")
            return {'text': '', 'confidence': 0.0, 'method': 'tesseract'}
    
    def extract_with_easyocr(self, image_path: str) -> Dict:
        """Extract text using EasyOCR."""
        try:
            # Read and extract text
            results = self.easyocr_reader.readtext(image_path)
            
            # Process results
            text_blocks = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > self.confidence_threshold:
                    text_blocks.append(text.strip())
                    confidences.append(confidence)
            
            extracted_text = ' '.join(text_blocks)
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                'text': extracted_text,
                'confidence': avg_confidence,
                'method': 'easyocr'
            }
        
        except Exception as e:
            logger.error(f"EasyOCR extraction error: {str(e)}")
            return {'text': '', 'confidence': 0.0, 'method': 'easyocr'}
    
    def extract_text(self, image_path: str) -> Dict:
        """Extract text using both OCR methods and return best result."""
        try:
            # Try both methods
            tesseract_result = self.extract_with_tesseract(image_path)
            easyocr_result = self.extract_with_easyocr(image_path)
            
            # Choose better result based on confidence
            if tesseract_result['confidence'] >= easyocr_result['confidence']:
                best_result = tesseract_result
                backup_result = easyocr_result
            else:
                best_result = easyocr_result
                backup_result = tesseract_result
            
            # Combine results if both have decent confidence
            if (best_result['confidence'] > 0.8 and backup_result['confidence'] > 0.6):
                combined_text = f"{best_result['text']} {backup_result['text']}"
                # Remove duplicates
                words = list(set(combined_text.split()))
                combined_text = ' '.join(words)
                
                return {
                    'text': combined_text,
                    'confidence': (best_result['confidence'] + backup_result['confidence']) / 2,
                    'method': 'combined',
                    'tesseract': tesseract_result,
                    'easyocr': easyocr_result
                }
            
            return {
                'text': best_result['text'],
                'confidence': best_result['confidence'],
                'method': best_result['method'],
                'tesseract': tesseract_result,
                'easyocr': easyocr_result
            }
        
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'error',
                'error': str(e)
            }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep medical abbreviations
            text = re.sub(r'[^\w\s\.\-\(\)\/]', '', text)
            
            # Fix common OCR errors
            text = text.replace('0', 'O').replace('1', 'I')  # Common OCR mistakes
            text = re.sub(r'\bmg\b', 'mg', text, flags=re.IGNORECASE)
            text = re.sub(r'\bml\b', 'ml', text, flags=re.IGNORECASE)
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"Text cleaning error: {str(e)}")
            return text

async def process_prescription_ocr(image_path: str) -> Dict:
    """Process prescription image and extract text."""
    try:
        ocr = PrescriptionOCR()
        result = ocr.extract_text(image_path)
        
        # Clean the extracted text
        if result['text']:
            result['cleaned_text'] = ocr.clean_text(result['text'])
        
        logger.info(f"OCR processing completed for {image_path}")
        return result
    
    except Exception as e:
        logger.error(f"OCR processing error for {image_path}: {str(e)}")
        return {
            'text': '',
            'confidence': 0.0,
            'method': 'error',
            'error': str(e)
        }