from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from src.core.database import get_db
from src.core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.models.user import User, Role
from src.schemas.user import UserCreate, UserOut, Token
from src.schemas.role import UserRole

# router initialization
router = APIRouter(prefix="/users", tags=["Users & Auth"])

# get Role ID (Ensures role exists)
async def get_role_id(session: AsyncSession, role_name: UserRole) -> int:
    """Fetches the primary key ID for a given role name."""
    result = await session.execute(
        select(Role.id).where(Role.name == role_name.value)
    )
    role_id = result.scalar_one_or_none()
    if role_id is None:
        # this error should only occur if the database seeding failed
        raise HTTPException(status_code=500, detail=f"Role '{role_name.value}' not found in database. Check seeding.")
    return role_id


# 1. Registration Endpoint (Initializes a new User) - Authentication
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    #checks if user already exists
    existing_user = (await db.execute(select(User).where(User.email == user_data.email))).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    # assigns default role ('user')
    user_role_id = await get_role_id(db, UserRole.user) 
    
    #creates the User record
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password), #hashed password
        role_id=user_role_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # returns the non-sensitive output data - this can be showed in the UI
    return UserOut(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        role_name=UserRole.user,
        is_active=db_user.is_active
    )


# 2. Login Endpoint (Issues JWT Token)
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # retrieves user by email (form_data.username contains the email)
    user = (await db.execute(select(User).where(User.email == form_data.username))).scalar_one_or_none()
    
    # verify credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3.create the JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        # The 'sub' claim (subject) must be a unique identifier, using email here
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # 4.return token
    return {"access_token": access_token, "token_type": "bearer"}