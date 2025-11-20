#so the purpose of this deps.py is to ensure that the requests from a logged in user who has the privileges
#we check that a user is valid at login, but we also have to make sure that the resources cannont be accessed if the user isnt logged

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import decode_access_token
from src.models.user import User

# --- 1. OAuth2 Bearer Scheme ---
# This tells FastAPI how to expect the token (in the Authorization header as "Bearer <token>")
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/users/token")


# 2. Get Current User Dependency (The Gatekeeper)
async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Decodes the JWT token from the Authorization header and retrieves the User object.
    
    If the token is invalid, expired, or the user is inactive, it raises a 401 error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decode the token using the secret key
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception # Token is invalid or expired

    # 2. Extract the user's identity (email) from the 'sub' claim
    user_email: str = payload.get("sub")
    if user_email is None:
        raise credentials_exception

    # 3. Look up the user in the database
    user = (await db.execute(select(User).where(User.email == user_email))).scalar_one_or_none()
    
    if user is None:
        raise credentials_exception # User not found
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Success: Return the full SQLAlchemy User object
    return user