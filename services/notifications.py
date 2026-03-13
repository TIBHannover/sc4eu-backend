from .push import send_push
import os
from models.push_subscription_model import PushSubscriptionModel
from urllib.parse import urlparse

VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")


def make_notify(db_session, payload):
    payload = payload
    subscriptions = db_session.query(PushSubscriptionModel).all()

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


def notify_new_term(db_session, update):
    payload = {
        "title": update,
        "body": "Placeholder text",
        "url": "/ocp/terms/PLACEHOLDER",
        "type": "TERMS_UPDATED",
    }

    make_notify(db_session, payload)


def notify_new_comment(db_session, update):
    payload = {
        "title": update,
        "body": "Placeholder text",
        "url": "/ocp/terms/PLACEHOLDER",
        "type": "COMMENTS_ADDED",
    }

    make_notify(db_session, payload)


def notify_new_vote(db_session, vote):
    payload = {
        "title": "New ontology vote created",
        "body": f"A new vote was created for term {vote.term_uuid}",
        "url": f"/ocp/terms/{vote.term_uuid}",
        "type": "VOTE_CREATED",
        "vote_id": str(vote.uuid),
    }

    make_notify(db_session, payload)


def notify_close_vote(db_session, vote):
    payload = {
        "title": "Vote has been closed",
        "body": f"Vote with {vote.term_uuid} has been closed by the administrator",
        "url": f"/ocp/terms/{vote.term_uuid}",
        "type": "VOTE_CLOSED",
        "vote_id": str(vote.uuid),
    }

    make_notify(db_session, payload)
