import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.services.auth import get_current_user
from app.services.cache import cache_service

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

def get_watchlist_cache_key(user_id: int) -> str:
    return f"watchlist:user_{user_id}"

@router.get("", response_model=List[WatchlistResponse])
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cache_key = get_watchlist_cache_key(current_user.id)
    
    # Try fetching from cache
    cached_data = cache_service.get(cache_key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except Exception:
            pass  # Fallback to database query if cache corruption
            
    # Database query
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    
    # Convert items to schemas to serialize appropriately (with camelCase aliases)
    items_schema = [WatchlistResponse.model_validate(item) for item in items]
    # Serialize to JSON using model_dump (by_alias=True ensures we use camelCase names in JSON)
    serialized = json.dumps([item.model_dump(by_alias=True) for item in items_schema])
    
    # Cache the result for 5 minutes
    cache_service.set(cache_key, serialized, expire=300)
    
    return items

@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if stock already exists in user's watchlist
    existing_item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id,
        WatchlistItem.symbol == watchlist_data.symbol.upper()
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {watchlist_data.symbol} is already in your watchlist."
        )

    new_item = WatchlistItem(
        user_id=current_user.id,
        symbol=watchlist_data.symbol.upper()
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Invalidate cache
    cache_service.delete(get_watchlist_cache_key(current_user.id))
    
    return new_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found"
        )
        
    db.delete(item)
    db.commit()
    
    # Invalidate cache
    cache_service.delete(get_watchlist_cache_key(current_user.id))
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
