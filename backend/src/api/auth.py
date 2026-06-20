import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from src.db.database import SessionLocal
from src.db import crud

# --- Configuration ---
# In production, these should be in .env
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- Models ---
class GoogleTokenRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(crud.User).filter(crud.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# --- Routes ---
@router.post("/google", response_model=TokenResponse)
def google_auth(request: GoogleTokenRequest, db = Depends(get_db)):
    try:
        # 1. Verify Google token
        idinfo = id_token.verify_oauth2_token(
            request.token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )

        # 2. Extract user info
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", "User")
        picture = idinfo.get("picture", "")

        # 3. Get or Create user in DB
        user = crud.get_or_create_user(db, google_id, email, name, picture)

        # 4. Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }
        }
    except ValueError as e:
        print(f"Token validation failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")

@router.get("/me")
def read_users_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url
    }
