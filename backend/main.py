"""
AI Prescription Analyzer - Main FastAPI Application
Healthcare platform for prescription analysis and drug interaction detection.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from loguru import logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import (
    auth,
    prescriptions, 
    interactions,
    pharmacy,
    chatbot,
    users,
    notifications
)

# Import middleware
from middleware.security import SecurityHeadersMiddleware
from middleware.logging import LoggingMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="AI Prescription Analyzer",
    description="AI-powered healthcare platform for prescription analysis and drug interaction detection",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/api/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,
)

# Security middleware
security = HTTPBearer()

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(prescriptions.router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])
app.include_router(interactions.router, prefix="/api/v1/interactions", tags=["Drug Interactions"])
app.include_router(pharmacy.router, prefix="/api/v1/pharmacy", tags=["Pharmacy"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["AI Chatbot"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "AI Prescription Analyzer API",
        "version": "1.0.0",
        "status": "active",
        "description": "Healthcare platform for prescription analysis and drug interaction detection"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("AI Prescription Analyzer API starting up...")
    
    # Initialize database connection
    # await database.connect()
    
    # Load AI models
    # await load_models()
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("AI Prescription Analyzer API shutting down...")
    
    # Close database connection
    # await database.disconnect()
    
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )