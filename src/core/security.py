from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from typing import Any

#reads from environment variables (set in .env)
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# CryptContext for password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

#password hashing functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    #compares plain-text password to the hashed one - we should use this at login
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    #function that hashes password - this should be used when creating new users (authentication)
    return pwd_context.hash(password)

#JWT token functions
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Creates a signed JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 'exp' (Expiration Time) claim is required for token security - aici ii cred pe cuvant
    to_encode.update({"exp": expire})
    
    # SECRET_KEY and ALGORITHM to sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodes and validates a JWT access token."""
    try:
        # decodes the token, verifying the signature using the SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        #stores the user's email under the 'sub' (Subject) claim - from what I understand 'sub' is used by JWT to uniquely identify an user and we use the email for this (no multiple accounts with the same email)
        email: str = payload.get("sub") 
        if email is None:
            return None
        return payload
        
    except JWTError:
        return None