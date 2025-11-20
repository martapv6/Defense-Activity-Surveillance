from sqlalchemy import Column, Integer, String, DateTime, func, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base 

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    # GEE Asset ID or internal tracking ID for the specific satellite scene
    asset_id = Column(String, unique=True, nullable=False) 
    
    # Metadata from the satellite data - aici mai trebuie vazut daca sunt parametrii corespunzatori
    source = Column(String) # e.g., 'Sentinel-2'
    acquisition_date = Column(DateTime, nullable=False)
    cloud_cover = Column(Float)
    resolution = Column(Float) # e.g., 10 (meters)
    
    # FK for SATELLITE_DATA table - not implemented yet
    # fk_data_id = Column(Integer, ForeignKey("satellite_data.id"))
    
    detections = relationship("Detection", back_populates="image")

    def __repr__(self):
        return f"<Image(asset_id='{self.asset_id}', date='{self.acquisition_date.strftime('%Y-%m-%d')}')>"