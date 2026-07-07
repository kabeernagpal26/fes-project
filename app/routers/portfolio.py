import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.portfolio import PortfolioItem
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioResponse
from app.services.auth import get_current_user
from app.services.cache import cache_service

router = APIRouter(prefix="/portfolio", tags=["Portfolio Management"])

def get_portfolio_cache_key(user_id: int) -> str:
    return f"portfolio:user_{user_id}"

@router.get("", response_model=List[PortfolioResponse])
def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cache_key = get_portfolio_cache_key(current_user.id)
    
    # Try fetching from cache
    cached_data = cache_service.get(cache_key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except Exception:
            pass  # Fallback to database query if cache corruption
            
    # Database query
    items = db.query(PortfolioItem).filter(PortfolioItem.user_id == current_user.id).all()
    
    # Convert items to schemas to serialize appropriately (with camelCase aliases)
    items_schema = [PortfolioResponse.model_validate(item) for item in items]
    # Serialize to JSON using model_dump (by_alias=True ensures we use camelCase names in JSON)
    serialized = json.dumps([item.model_dump(by_alias=True) for item in items_schema])
    
    # Cache the result for 5 minutes
    cache_service.set(cache_key, serialized, expire=300)
    
    return items

@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def add_portfolio_item(
    item_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if stock already exists in user's portfolio
    existing_item = db.query(PortfolioItem).filter(
        PortfolioItem.user_id == current_user.id,
        PortfolioItem.stock_symbol == item_data.stock_symbol.upper()
    ).first()
    
    if existing_item:
        # Instead of failing, we can either raise bad request or combine them.
        # Let's raise an HTTP 400 as standard practice, or update. Let's raise 400.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock {item_data.stock_symbol} already exists in portfolio. Use PUT to modify."
        )

    new_item = PortfolioItem(
        user_id=current_user.id,
        stock_symbol=item_data.stock_symbol.upper(),
        quantity=item_data.quantity,
        average_price=item_data.average_price
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Invalidate cache
    cache_service.delete(get_portfolio_cache_key(current_user.id))
    
    return new_item

@router.put("/{item_id}", response_model=PortfolioResponse)
def update_portfolio_item(
    item_id: int,
    item_data: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(PortfolioItem).filter(
        PortfolioItem.id == item_id,
        PortfolioItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found"
        )
        
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    if item_data.average_price is not None:
        item.average_price = item_data.average_price
        
    db.commit()
    db.refresh(item)
    
    # Invalidate cache
    cache_service.delete(get_portfolio_cache_key(current_user.id))
    
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(PortfolioItem).filter(
        PortfolioItem.id == item_id,
        PortfolioItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found"
        )
        
    db.delete(item)
    db.commit()
    
    # Invalidate cache
    cache_service.delete(get_portfolio_cache_key(current_user.id))
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
