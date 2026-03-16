from extensions import db
from ._base import ModelMixin

class PushSubscriptionModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_push_subscription_model'

    id = db.Column("hash_id", db.Integer, primary_key=True, unique=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("sc3_user_model.hash_id"), nullable=False
    )
    endpoint = db.Column(db.String, nullable=False)
    p256dh = db.Column(db.String, nullable=False)
    auth = db.Column(db.String, nullable=False)

    user = db.relationship("UserModel", back_populates="subscriptions")

    def __init__(self, **kwargs):
        super(PushSubscriptionModel, self).__init__(**kwargs)