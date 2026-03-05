import json
from .push import send_push
import os


def notify_new_vote(db, vote):
    payload = {
        "title": "New ontology vote created",
        "body": f"A new vote was created for term {vote.term_uuid}",
        "url": f"/ocp/terms/{vote.term_uuid}",
        "type": "VOTE_CREATED",
        "vote_id": str(vote.uuid),
    }

    print(f"\nPayload size: {len(json.dumps(payload))} bytes")

    from models.push_subscription_model import PushSubscriptionModel

    subscriptions = (
        db.query(PushSubscriptionModel).filter_by(user_id=vote.user_id).all()
    )

    if not subscriptions:
        return {"total": 0, "successful": 0, "expired": 0}

    # VAPID configuration
    VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
    VAPID_CLAIMS = {"sub": "mailto:admin@example.com"}

    results = []
    expired_subscriptions = []

    for i, sub in enumerate(subscriptions):
        print(f"\n{'─' * 60}")
        print(f"Processing subscription {i + 1}/{len(subscriptions)}")
        print(f"{'─' * 60}")
        print(f"Subscription ID: {sub.id}")
        print(f"Endpoint: {sub.endpoint[:80]}...")
        print(f"p256dh length: {len(sub.p256dh) if sub.p256dh else 0}")
        print(f"auth length: {len(sub.auth) if sub.auth else 0}")

        # Validate subscription data
        if not sub.endpoint:
            print(f"❌ Missing endpoint!")
            results.append(False)
            continue

        if not sub.p256dh or not sub.auth:
            print(f"❌ Missing encryption keys!")
            results.append(False)
            continue

        result = send_push(
            subscription={
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            },
            payload=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )

        if result == "expired":
            expired_subscriptions.append(sub)

        results.append(result)

    if expired_subscriptions:
        print(f"\n{'─' * 60}")
        print(f"Removing {len(expired_subscriptions)} expired subscription(s)")
        for sub in expired_subscriptions:
            print(f"  Removing subscription {sub.id}")
            db.delete(sub)
        db.commit()
        print(f"✅ Expired subscriptions removed")

    success_count = sum(1 for r in results if r is True)

    return {
        "total": len(subscriptions),
        "successful": success_count,
        "expired": len(expired_subscriptions),
    }
