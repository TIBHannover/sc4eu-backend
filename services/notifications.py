import os
from typing import Optional
from urllib.parse import urlparse

from models.enums.term_update_type import TermUpdateType
from models.push_subscription_model import PushSubscriptionModel
from models.user_model import UserModel

from .push import send_push

VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
CLIENT_PUBLIC_URL = os.environ.get("CLIENT_PUBLIC_URL")

def make_notify(db_session, payload, user_names: list[str] | None = None):
    query = db_session.query(PushSubscriptionModel)

    if user_names:
        mentioned_ids = [
            user.id
            for user in db_session.query(UserModel).filter(
                UserModel.display_name.in_(user_names)
            )
        ]
        query = query.filter(PushSubscriptionModel.user_id.in_(mentioned_ids))

    subscriptions = query.all()

    if not subscriptions:
        return {"total": 0, "successful": 0, "expired": 0}

    results = []
    expired_subscriptions = []

    for i, sub in enumerate(subscriptions):
        if not sub.endpoint:
            results.append(False)
            continue

        if not sub.p256dh or not sub.auth:
            results.append(False)
            continue

        result = send_push(
            subscription={
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            },
            payload=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": "mailto:admin@example.com",
                "aud": urlparse(sub.endpoint).scheme
                + "://"
                + urlparse(sub.endpoint).netloc,
            },
        )

        if result == "expired":
            expired_subscriptions.append(sub)

        results.append(result)

    if expired_subscriptions:
        for sub in expired_subscriptions:
            db_session.delete(sub)
        db_session.commit()

    success_count = sum(1 for r in results if r is True)

    return {
        "total": len(subscriptions),
        "successful": success_count,
        "expired": len(expired_subscriptions),
    }


def notify_term_update(db_session, title, body, term_uuid, type):
    notification_url = f"{CLIENT_PUBLIC_URL}/vocabulary_support/terms/{term_uuid}"
    if type == TermUpdateType.Delete:
        notification_url = "{CLIENT_PUBLIC_URL}/vocabulary_support/"

    payload = {
        "title": title,
        "body": body,
        "url": notification_url,
        "type": "TERMS_UPDATED",
    }

    make_notify(db_session, payload)


def notify_new_comment(db_session, title, term_uuid, mentioned_user_names):
    payload = {
        "title": title,
        "body": "You were mentioned in a term",
        "url": f"{CLIENT_PUBLIC_URL}/vocabulary_support/terms/{term_uuid}",
        "type": "COMMENTS_ADDED",
    }

    make_notify(db_session, payload, mentioned_user_names)


def notify_new_vote(db_session, vote):
    payload = {
        "title": f"A new vote was created for term {vote.term_uuid}",
        "body": "Click to see",
        "url": f"{CLIENT_PUBLIC_URL}/vocabulary_support/terms/{vote.term_uuid}/consensuses/{vote.uuid}",
        "type": "VOTE_CREATED",
        "vote_id": str(vote.uuid),
    }

    make_notify(db_session, payload)


def notify_close_vote(db_session, vote):
    payload = {
        "title": "Vote has been closed",
        "body": f"Vote with {vote.term_uuid} has been closed by the administrator",
        "url": f"{CLIENT_PUBLIC_URL}/vocabulary_support/terms/{vote.term_uuid}",
        "type": "VOTE_CLOSED",
        "vote_id": str(vote.uuid),
    }

    make_notify(db_session, payload)
