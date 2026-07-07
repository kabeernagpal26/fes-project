from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema

class PortfolioCreate(BaseSchema):
    stock_symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    average_price: float = Field(..., gt=0, description="Average buy price must be greater than 0")

class PortfolioUpdate(BaseSchema):
    quantity: Optional[int] = Field(None, gt=0, description="Updated quantity (must be greater than 0)")
    average_price: Optional[float] = Field(None, gt=0, description="Updated average buy price (must be greater than 0)")

class PortfolioResponse(BaseSchema):
    id: int
    user_id: int
    stock_symbol: str
    quantity: int
    average_price: float
