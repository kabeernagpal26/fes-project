from typing import Literal
from pydantic import Field
from app.schemas.base import BaseSchema

class AlertCreate(BaseSchema):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    condition: Literal["above", "below"] = Field(..., description="Alert threshold condition: 'above' or 'below'")
    target_price: float = Field(..., gt=0, description="Target price threshold (must be greater than 0)")

class AlertResponse(BaseSchema):
    id: int
    user_id: int
    symbol: str
    condition: Literal["above", "below"]
    target_price: float
