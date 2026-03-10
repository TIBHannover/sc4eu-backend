from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from backend.models.user_model import UserModel
from models.push_subscription_model import PushSubscriptionModel
from sqlalchemy.orm import Session
from extensions import get_db

notification_router = APIRouter(prefix="/api/push", tags=["notifications"])


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class SubscribeObject(BaseModel):
    username: str
    endpoint: str
    keys: PushSubscriptionKeys
    reason: Optional[List[str]] = None


@notification_router.post("/subscribe")
async def create_new_push(
    payload: SubscribeObject = Body(
        description="Body with choice, user_name and comment (optional)"
    ),
    db_session: Session = Depends(get_db),
):
    print(f"Endpoint called with {payload.endpoint}")

    user = db_session.query(UserModel).filter_by(display_name=payload.username).first()
    
    if not user:
        raise HTTPException(
            status_code=400, detail=f"User with username {payload.username} not found")

    subscription = PushSubscriptionModel(
        user_id=user.id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
    )

    db_session.add(subscription)
    db_session.commit()
