from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from src.core.database import Base 

class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    score = Column(Float) # Confidence score of the anomaly
    type = Column(String) # e.g., 'construction', 'vehicle_movement'
    
    # PostGIS Column: The precise location/polygon of the detected anomaly within the AOI
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    
    # FKs linking to other tables:
    aoi_id = Column(Integer, ForeignKey("areas_of_interest.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("model_ai.id"), nullable=False)
    
    # Relationships
    aoi = relationship("AreaOfInterest")
    image = relationship("Image", back_populates="detections")
    model = relationship("ModelAI", back_populates="detections")
    alerts = relationship("Alert", back_populates="detection")

    def __repr__(self):
        return f"<Detection(score={self.score}, aoi_id={self.aoi_id})>"