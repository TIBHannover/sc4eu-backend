from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from models.user_model import UserModel
from models.push_subscription_model import PushSubscriptionModel
from sqlalchemy.orm import Session
from extensions import get_db
from services.notifications import notify_new_term

notification_router = APIRouter(prefix="/api/push", tags=["notifications"])


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class SubscribeObject(BaseModel):
    username: str
    endpoint: str
    keys: PushSubscriptionKeys
    reason: Optional[List[str]] = None

class UnsubscribeObject(BaseModel):
    endpoint: str

class UpdateTermObject(BaseModel):
    update: str

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

    existing_sub = db_session.query(PushSubscriptionModel).filter_by(endpoint=payload.endpoint).first()

    if existing_sub:
        existing_sub.p256dh = payload.keys.p256dh
        existing_sub.auth = payload.keys.auth
    else:
        subscription = PushSubscriptionModel(
            user_id=user.id,
            endpoint=payload.endpoint,
            p256dh=payload.keys.p256dh,
            auth=payload.keys.auth,
        )
        db_session.add(subscription)
    
    db_session.commit() 

@notification_router.post("/unsubscribe")
async def remove_existing_push(
    payload: UnsubscribeObject = Body(description="Endpoint associated with push subscription"),
    db_session: Session = Depends(get_db),
):
    print(f"Endpoint called with {payload.endpoint}")

    db_session.query(PushSubscriptionModel).filter_by(endpoint=payload.endpoint).delete()
    db_session.commit()

@notification_router.post("/notifyTerms")
async def notify_existing_terms(
    payload: UpdateTermObject = Body(description="Update that happened with terms in vocabualary"),
    db_session: Session = Depends(get_db),
):
    print(f"Endpoint called with {payload.update}")

    notify_new_term(db_session, payload.update)
