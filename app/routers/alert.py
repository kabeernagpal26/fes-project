from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alert Management"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    return alerts

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if duplicate alert exists for user
    duplicate = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.symbol == alert_data.symbol.upper(),
        Alert.condition == alert_data.condition,
        Alert.target_price == alert_data.target_price
    ).first()
    
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An identical price alert already exists for this symbol."
        )

    new_alert = Alert(
        user_id=current_user.id,
        symbol=alert_data.symbol.upper(),
        condition=alert_data.condition,
        target_price=alert_data.target_price
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
        
    db.delete(alert)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
