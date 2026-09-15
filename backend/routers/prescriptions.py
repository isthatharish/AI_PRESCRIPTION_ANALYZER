"""
Prescription router for handling prescription uploads, OCR processing, and analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

from routers.auth import get_current_user
from services.ocr_service import process_prescription_ocr

router = APIRouter()

# Pydantic models
class PrescriptionCreate(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    doctor_name: Optional[str] = None
    notes: Optional[str] = None

class PrescriptionResponse(BaseModel):
    id: str
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    doctor_name: Optional[str]
    notes: Optional[str]
    extracted_text: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    patient_email: str

class OCRResult(BaseModel):
    extracted_text: str
    confidence_score: float
    structured_data: dict

@router.post("/upload", response_model=dict)
async def upload_prescription(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload prescription image/PDF for OCR processing."""
    try:
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and PDF files are allowed.")
        
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Save file temporarily (in real implementation, save to secure storage)
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Process with OCR
        try:
            ocr_result = await process_prescription_ocr(file_path)
            
            # Check if OCR was successful
            if ocr_result["confidence_score"] < 0.3:
                raise HTTPException(
                    status_code=400, 
                    detail="Unable to extract text from image. Please ensure the image is clear and contains prescription text."
                )
        except Exception as ocr_error:
            # Clean up uploaded file on OCR error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {str(ocr_error)}"
            )
        
        # Save prescription to database (placeholder)
        prescription_id = f"rx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Clean up uploaded file after processing (optional - you may want to keep files)
        # os.remove(file_path)
        
        return {
            "message": "Prescription uploaded and processed successfully",
            "prescription_id": prescription_id,
            "ocr_result": ocr_result,
            "file_name": file.filename,
            "patient_email": current_user["email"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create", response_model=dict)
async def create_prescription(
    prescription: PrescriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create prescription manually (without OCR)."""
    try:
        # Save prescription to database (placeholder)
        prescription_id = f"rx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        prescription_data = {
            "id": prescription_id,
            "medication_name": prescription.medication_name,
            "dosage": prescription.dosage,
            "frequency": prescription.frequency,
            "duration": prescription.duration,
            "doctor_name": prescription.doctor_name,
            "notes": prescription.notes,
            "created_at": datetime.utcnow(),
            "patient_email": current_user["email"]
        }
        
        # In real implementation: save to database
        # db_prescription = create_prescription_record(prescription_data)
        
        return {
            "message": "Prescription created successfully",
            "prescription_id": prescription_id,
            "prescription_data": prescription_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[dict])
async def get_prescriptions(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """Get user's prescriptions."""
    try:
        # In real implementation: fetch from database
        # prescriptions = get_user_prescriptions(current_user["email"], limit, offset)
        
        # Mock prescriptions for demo
        mock_prescriptions = [
            {
                "id": "rx_20240101_120000",
                "medication_name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "3 times daily",
                "duration": "7 days",
                "doctor_name": "Dr. Smith",
                "created_at": "2024-01-01T12:00:00Z",
                "patient_email": current_user["email"]
            },
            {
                "id": "rx_20240101_140000",
                "medication_name": "Ibuprofen",
                "dosage": "200mg",
                "frequency": "As needed",
                "duration": "14 days",
                "doctor_name": "Dr. Johnson",
                "created_at": "2024-01-01T14:00:00Z",
                "patient_email": current_user["email"]
            }
        ]
        
        return mock_prescriptions
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{prescription_id}", response_model=dict)
async def get_prescription(
    prescription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific prescription details."""
    try:
        # In real implementation: fetch from database
        # prescription = get_prescription_by_id(prescription_id)
        # if not prescription or prescription.patient_email != current_user["email"]:
        #     raise HTTPException(status_code=404, detail="Prescription not found")
        
        # Mock prescription for demo
        mock_prescription = {
            "id": prescription_id,
            "medication_name": "Amoxicillin",
            "dosage": "500mg",
            "frequency": "3 times daily",
            "duration": "7 days",
            "doctor_name": "Dr. Smith",
            "notes": "Take with food",
            "created_at": "2024-01-01T12:00:00Z",
            "patient_email": current_user["email"]
        }
        
        return mock_prescription
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{prescription_id}")
async def delete_prescription(
    prescription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a prescription."""
    try:
        # In real implementation: delete from database
        # prescription = get_prescription_by_id(prescription_id)
        # if not prescription or prescription.patient_email != current_user["email"]:
        #     raise HTTPException(status_code=404, detail="Prescription not found")
        # delete_prescription_record(prescription_id)
        
        return {
            "message": "Prescription deleted successfully",
            "prescription_id": prescription_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{prescription_id}/analyze")
async def analyze_prescription(
    prescription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Analyze prescription for drug interactions and safety."""
    try:
        # In real implementation: fetch prescription and analyze
        # prescription = get_prescription_by_id(prescription_id)
        # analysis_result = analyze_drug_interactions(prescription)
        
        # Mock analysis result
        mock_analysis = {
            "prescription_id": prescription_id,
            "safety_score": 85,
            "interactions": [
                {
                    "severity": "moderate",
                    "description": "May increase drowsiness when combined with alcohol",
                    "recommendation": "Avoid alcohol during treatment"
                }
            ],
            "age_appropriate": True,
            "dosage_recommendation": "Current dosage is appropriate for adult patients",
            "alternatives": [
                {
                    "medication": "Azithromycin",
                    "reason": "Alternative antibiotic with fewer side effects"
                }
            ]
        }
        
        return mock_analysis
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))