from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from src.core.database import Base 

# AreaOfInterest Model (User's monitored polygon)
class AreaOfInterest(Base):
    __tablename__ = "areas_of_interest"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    
    # Link to the User who created this AOI
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # PostGIS Geospatial Column (Requires the PostGIS extension to be enabled!)
    # geometry_type='MULTIPOLYGON' handles complex areas.
    # srid=4326 is the standard WGS 84 (GPS coordinates).
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)
    
    # Monitoring status (basically if the current area of interest is monitored at the moment)
    is_active = Column(Boolean, default=True) 
    
    created_at = Column(DateTime, server_default=func.now())

    # Define relationships
    owner = relationship("User", back_populates="areas_of_interest")
    # detections = relationship("Detection", back_populates="aoi") # Will be added later

    def __repr__(self):
        return f"<AOI(name='{self.name}', user_id={self.user_id})>"