from sqlalchemy import Column, Integer, String, DateTime, Float, func
from sqlalchemy.orm import relationship
from src.core.database import Base 

class ModelAI(Base):
    __tablename__ = "model_ai"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g., 'Satlas Anomaly Detector'
    version = Column(String, unique=True, nullable=False) # e.g., 'v1.2.0'
    date = Column(DateTime, server_default=func.now())
    false_positive_rate = Column(Float) # Key metric for the model
    
    detections = relationship("Detection", back_populates="model")

    def __repr__(self):
        return f"<Model(name='{self.name}', version='{self.version}')>"