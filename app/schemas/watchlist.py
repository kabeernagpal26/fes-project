from pydantic import Field
from app.schemas.base import BaseSchema

class WatchlistCreate(BaseSchema):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol to watch")

class WatchlistResponse(BaseSchema):
    id: int
    user_id: int
    symbol: str
