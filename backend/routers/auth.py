"""
Authentication router for user login, registration, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "patient"  # patient, doctor, pharmacist
    age: Optional[int] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception
    
    # Here you would typically fetch user from database
    # user = get_user_by_email(email=token_data.email)
    # if user is None:
    #     raise credentials_exception
    
    return {"email": email, "role": role}

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    """Register a new user."""
    try:
        # Check if user already exists (in real implementation, check database)
        # existing_user = get_user_by_email(user.email)
        # if existing_user:
        #     raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user in database (placeholder)
        user_data = {
            "email": user.email,
            "hashed_password": hashed_password,
            "full_name": user.full_name,
            "role": user.role,
            "age": user.age,
            "phone": user.phone,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # In real implementation: save to database
        # db_user = create_user(user_data)
        
        return {
            "message": "User registered successfully",
            "email": user.email,
            "role": user.role
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    """Authenticate user and return JWT token."""
    try:
        # In real implementation: fetch user from database
        # db_user = get_user_by_email(user.email)
        # if not db_user or not verify_password(user.password, db_user.hashed_password):
        #     raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        # For demo purposes, accept any login
        if user.email and user.password:
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "role": "patient"},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "email": current_user["email"],
        "role": current_user["role"],
        "message": "User authenticated successfully"
    }

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (in real implementation, invalidate token)."""
    return {
        "message": "Successfully logged out",
        "email": current_user["email"]
    }

@router.post("/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token."""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user["email"], "role": current_user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))