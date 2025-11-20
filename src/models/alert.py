from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.core.database import Base 

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    # Status of the alert: 'new', 'sent', 'viewed', 'dismissed'
    status = Column(String, default="new") 
    type = Column(String)
    
    # Link to the detection that triggered this alert
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=False)
    
    # Note: Since the detection is already linked to an Area of Interest(AOI), which is linked to a User, we don't need a direct FK to User unless we want to track a separate notification recipient.
    
    # Relationships
    detection = relationship("Detection", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, status='{self.status}')>"