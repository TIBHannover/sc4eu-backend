from typing import List, Optional
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from models.push_subscription_model import PushSubscriptionModel
from sqlalchemy.orm import Session
from extensions import get_db

notification_router = APIRouter(prefix="/api/push", tags=["notifications"])


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class SubscribeObject(BaseModel):
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
    subscription = PushSubscriptionModel(
        user_id=1,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
    )

    db_session.add(subscription)
    db_session.commit()
