"""
Debug script to identify OCR extraction issues
This will help us understand what's going wrong with text extraction
"""

import asyncio
import os
import sys
import traceback
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_test_image():
    """Create a very simple test prescription image with clear text"""
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use default font (more reliable)
    try:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        font_large = None
        font_small = None
    
    # Add very clear, simple text
    lines = [
        "PRESCRIPTION",
        "",
        "Dr. John Smith",
        "",
        "Amoxicillin 500mg",
        "Take 3 times daily",
        "For 7 days",
        "",
        "Patient: Jane Doe"
    ]
    
    y_pos = 30
    for line in lines:
        if line:
            draw.text((30, y_pos), line, fill='black', font=font_large)
        y_pos += 35
    
    filename = "debug_prescription.png"
    img.save(filename)
    print(f"Created test image: {filename}")
    return filename

async def test_easyocr_only():
    """Test EasyOCR only to isolate the issue"""
    print("\n=== Testing EasyOCR directly ===")
    
    try:
        import easyocr
        reader = easyocr.Reader(['en'], verbose=False)
        
        # Create test image
        test_image = create_simple_test_image()
        
        # Read image with OpenCV
        image = cv2.imread(test_image)
        if image is None:
            print("❌ Could not load test image with OpenCV")
            return False
            
        print(f"✅ Image loaded: {image.shape}")
        
        # Try EasyOCR
        print("Running EasyOCR...")
        results = reader.readtext(image, detail=1)
        
        print(f"EasyOCR found {len(results)} text regions:")
        for i, (bbox, text, conf) in enumerate(results):
            print(f"  {i+1}. Text: '{text}' (confidence: {conf:.2f})")
        
        # Clean up
        os.remove(test_image)
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ EasyOCR test failed: {str(e)}")
        traceback.print_exc()
        return False

async def test_our_ocr_service():
    """Test our OCR service implementation"""
    print("\n=== Testing Our OCR Service ===")
    
    try:
        from services.ocr_service import PrescriptionOCR
        
        # Create test image
        test_image = create_simple_test_image()
        
        ocr = PrescriptionOCR()
        result = await ocr.process_prescription(test_image)
        
        print(f"OCR Engine: {result.ocr_engine}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Raw text: '{result.raw_text}'")
        print(f"Structured data: {result.structured_data}")
        
        # Clean up
        os.remove(test_image)
        return result.confidence_score > 0
        
    except Exception as e:
        print(f"❌ OCR service test failed: {str(e)}")
        traceback.print_exc()
        if os.path.exists("debug_prescription.png"):
            os.remove("debug_prescription.png")
        return False

async def test_preprocessing():
    """Test image preprocessing"""
    print("\n=== Testing Image Preprocessing ===")
    
    try:
        from services.ocr_service import PrescriptionOCR
        
        # Create test image
        test_image = create_simple_test_image()
        
        ocr = PrescriptionOCR()
        processed_image, steps = ocr.preprocess_image(test_image)
        
        print(f"Preprocessing steps: {steps}")
        print(f"Processed image shape: {processed_image.shape}")
        print(f"Image dtype: {processed_image.dtype}")
        
        # Save processed image for inspection
        cv2.imwrite("processed_debug.png", processed_image)
        print("Saved processed image as 'processed_debug.png'")
        
        # Clean up
        os.remove(test_image)
        return True
        
    except Exception as e:
        print(f"❌ Preprocessing test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test all OCR dependencies"""
    print("\n=== Testing Dependencies ===")
    
    deps = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'), 
        ('PIL', 'Pillow'),
        ('easyocr', 'EasyOCR'),
        ('pytesseract', 'Pytesseract')
    ]
    
    issues = []
    for module_name, display_name in deps:
        try:
            module = __import__(module_name)
            print(f"✅ {display_name}: {getattr(module, '__version__', 'installed')}")
        except ImportError as e:
            issues.append(f"❌ {display_name}: Not installed ({e})")
        except Exception as e:
            issues.append(f"⚠️  {display_name}: Issue ({e})")
    
    if issues:
        print("\nDependency Issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    return True

async def main():
    print("AI Prescription Analyzer - OCR Debug Tool")
    print("=" * 50)
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependency issues found. Please fix them first.")
        return
    
    # Test EasyOCR directly
    easyocr_ok = await test_easyocr_only()
    
    # Test preprocessing
    preprocessing_ok = await test_preprocessing()
    
    # Test our service
    service_ok = await test_our_ocr_service()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS RESULTS:")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"EasyOCR Direct: {'✅' if easyocr_ok else '❌'}")
    print(f"Preprocessing: {'✅' if preprocessing_ok else '❌'}")
    print(f"OCR Service: {'✅' if service_ok else '❌'}")
    
    if not easyocr_ok:
        print("\n🔍 ISSUE: EasyOCR is not working properly")
        print("SOLUTIONS:")
        print("1. Check internet connection (EasyOCR needs to download models)")
        print("2. Try: pip install --upgrade easyocr")
        print("3. Clear EasyOCR cache: rm -rf ~/.EasyOCR")
    elif not service_ok:
        print("\n🔍 ISSUE: OCR service implementation has problems")
        print("SOLUTIONS:")
        print("1. Check the error messages above")
        print("2. Verify image preprocessing")
        print("3. Check text parsing logic")
    else:
        print("\n✅ All tests passed! OCR should be working.")
        print("If you're still having issues, please share:")
        print("1. The specific error message you're getting")
        print("2. A sample image you're trying to process")
    
    # Clean up any remaining files
    for file in ["debug_prescription.png", "processed_debug.png"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    asyncio.run(main())