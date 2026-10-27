from typing import List, Optional
from uuid import UUID

from extensions import get_db
from fastapi import APIRouter, Body, Depends, HTTPException
from models.push_subscription_model import PushSubscriptionModel
from models.user_model import UserModel
from pydantic import BaseModel
from services.notifications import notify_new_comment, notify_term_update
from sqlalchemy.orm import Session

from models.enums.term_update_type import TermUpdateType

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
    title: str
    body: str
    update_type: TermUpdateType
    term_uuid: UUID
class NewMentionCommentObject(BaseModel):
    title: str
    term_uuid: UUID
    mentioned_user_names: List[str]

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
    print(f"Endpoint called with {payload.title}")

    notify_term_update(db_session, payload.title, payload.body, payload.term_uuid, payload.update_type)

@notification_router.post("/notifyComments")
async def notify_new_comments(
    payload: NewMentionCommentObject = Body(description="New comment update object"),
    db_session: Session = Depends(get_db),
):
    print(f"Endpoint called with {payload.title}")

    notify_new_comment(db_session, payload.title, payload.term_uuid, payload.mentioned_user_names)