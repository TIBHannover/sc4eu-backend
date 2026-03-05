import json
from pywebpush import webpush, WebPushException
import traceback

def send_push(subscription, payload, vapid_private_key, vapid_claims):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
        )        
        return True
        
    except WebPushException:
        traceback.print_exc()
        return False
        
    except Exception:
        traceback.print_exc()
        return False
