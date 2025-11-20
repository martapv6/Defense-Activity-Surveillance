# app/models/user.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from src.core.database import Base 


#Role lookup table used for permisions
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    #'admin', 'user'
    name = Column(String, unique=True, nullable=False) 
    description = Column(String)

    # Define a relationship back to User
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


#User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False) 
    hashed_password = Column(String, nullable=False) # Stores the hashed password
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # FK to Role
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Define relationships
    role = relationship("Role", back_populates="users")
    areas_of_interest = relationship("AreaOfInterest", back_populates="owner")

    def __repr__(self):
        return f"<User(email='{self.email}')>"