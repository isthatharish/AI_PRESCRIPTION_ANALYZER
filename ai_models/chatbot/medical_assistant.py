"""
AI Medical Assistant using IBM Granite and Hugging Face models.
"""

import os
import httpx
from typing import Dict, List
from loguru import logger

class MedicalAssistant:
    """AI-powered medical assistant for prescription and health queries."""
    
    def __init__(self):
        """Initialize the medical assistant with API keys."""
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.ibm_granite_model = os.getenv("IBM_GRANITE_MODEL", "ibm-granite/granite-3.3-2b-base")
        self.hf_base_url = "https://api-inference.huggingface.co/models/"
        
    async def get_medical_response(self, query: str, context: Dict = None) -> str:
        """Generate medical response using AI models."""
        try:
            # Use Hugging Face medical model for response
            response = await self._query_huggingface(query, context)
            
            if response:
                return response
            else:
                # Fallback to basic medical responses
                return self._get_fallback_response(query)
        
        except Exception as e:
            logger.error(f"Medical assistant error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please consult with your healthcare provider for medical advice."
    
    async def _query_huggingface(self, query: str, context: Dict = None) -> str:
        """Query Hugging Face models for medical responses."""
        try:
            if not self.hf_api_key:
                return None
            
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            # Use a medical-focused model
            model_url = f"{self.hf_base_url}microsoft/DialoGPT-medium"
            
            # Prepare medical context
            medical_prompt = self._prepare_medical_prompt(query, context)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    model_url,
                    headers=headers,
                    json={"inputs": medical_prompt, "parameters": {"max_length": 200}}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "").strip()
                    elif isinstance(result, dict):
                        return result.get("generated_text", "").strip()
        
        except Exception as e:
            logger.error(f"Hugging Face query error: {str(e)}")
        
        return None
    
    def _prepare_medical_prompt(self, query: str, context: Dict = None) -> str:
        """Prepare medical-focused prompt with context."""
        prompt = f"Medical Assistant: I'm here to help with medication and health questions. "
        
        if context and context.get("current_medications"):
            medications = ", ".join(context["current_medications"])
            prompt += f"Your current medications include: {medications}. "
        
        prompt += f"Question: {query}\nResponse: "
        
        return prompt
    
    def _get_fallback_response(self, query: str) -> str:
        """Provide fallback medical responses for common queries."""
        query_lower = query.lower()
        
        # Common medical responses
        if "side effect" in query_lower:
            return ("Common side effects can vary by medication. Always read the medication label and "
                   "consult your pharmacist or doctor if you experience any unusual symptoms. "
                   "Severe side effects should be reported to your healthcare provider immediately.")
        
        elif "dosage" in query_lower or "how much" in query_lower:
            return ("Dosage depends on many factors including your age, weight, medical condition, and "
                   "other medications. Never change your dosage without consulting your healthcare provider. "
                   "Always follow the instructions on your prescription label.")
        
        elif "interaction" in query_lower:
            return ("Drug interactions can be serious. Always inform your healthcare providers about all "
                   "medications, supplements, and herbal products you're taking. Our interaction checker "
                   "can help identify potential issues, but always consult your pharmacist or doctor.")
        
        elif "when to take" in query_lower or "timing" in query_lower:
            return ("Medication timing is important for effectiveness. Follow your prescription label exactly. "
                   "Some medications should be taken with food, others on an empty stomach. "
                   "If you're unsure, consult your pharmacist.")
        
        elif "missed dose" in query_lower:
            return ("If you miss a dose, take it as soon as you remember, unless it's almost time for your "
                   "next dose. Don't double up on doses. Each medication has specific guidelines for missed doses, "
                   "so check with your pharmacist or the medication information.")
        
        elif "alcohol" in query_lower:
            return ("Many medications can interact with alcohol, potentially causing serious side effects or "
                   "reducing the medication's effectiveness. Always check with your healthcare provider or "
                   "pharmacist about alcohol consumption while taking any medication.")
        
        else:
            return ("For specific medical advice about your medications, please consult with your healthcare provider, "
                   "pharmacist, or use our prescription analysis features. I can help with general information about "
                   "drug interactions, side effects, and medication management.")

async def get_ai_medical_response(query: str, user_context: Dict = None) -> str:
    """Get AI-powered medical response."""
    try:
        assistant = MedicalAssistant()
        response = await assistant.get_medical_response(query, user_context)
        
        # Add disclaimer
        disclaimer = "\n\n⚠️ This is for informational purposes only and not a substitute for professional medical advice."
        return response + disclaimer
    
    except Exception as e:
        logger.error(f"AI medical response error: {str(e)}")
        return ("I apologize, but I'm currently unable to process your request. "
               "Please consult with your healthcare provider for medical advice.")

# Quick responses for common medical questions
QUICK_MEDICAL_RESPONSES = {
    "emergency": {
        "response": "🚨 For medical emergencies, call 911 immediately. This includes severe allergic reactions, chest pain, difficulty breathing, or any life-threatening symptoms.",
        "priority": "emergency"
    },
    "side_effects_severe": {
        "response": "⚠️ Severe side effects like difficulty breathing, swelling, severe rash, or chest pain require immediate medical attention. Call 911 or go to the emergency room.",
        "priority": "urgent"
    },
    "medication_safety": {
        "response": "💊 Always take medications as prescribed. Never share prescription medications with others. Store medications properly and check expiration dates regularly.",
        "priority": "important"
    }
}