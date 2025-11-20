from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

#database url from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

#SQLAlchemy Base class
Base = declarative_base()

# echo=True prints SQL queries to the console (good for debugging)
engine = create_async_engine(DATABASE_URL, echo=True)

# expire_on_commit=False prevents objects from being "detached" after commit
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

# Dependency for FastAPI endpoints to get a DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Function to be called during FastAPI startup lifespan event
async def create_db_and_tables():
    """Creates all tables defined by Base metadata."""
    async with engine.begin() as conn:
        # This checks Base.metadata and creates tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/checked.")