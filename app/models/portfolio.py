from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stock_symbol = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios")
