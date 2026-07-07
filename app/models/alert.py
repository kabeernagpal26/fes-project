from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, index=True, nullable=False)
    condition = Column(String, nullable=False)  # "above" or "below"
    target_price = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
