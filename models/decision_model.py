from extensions import db
from models._base import ModelMixin
from models.enums.vote_status import VoteStatus
from sqlalchemy import UniqueConstraint

class DecisionModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_decision_model'

    vote_id = db.Column(db.Integer, db.ForeignKey('sc3_vote_model.hash_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sc3_user_model.hash_id'), primary_key=True)

    comment = db.Column(db.String, nullable=True)
    choice = db.Column(db.String, nullable=True)

    vote = db.relationship('VoteModel', back_populates='decisions')
    user = db.relationship('UserModel', back_populates='decisions')

    __table_args__ = (
        UniqueConstraint('user_id', 'vote_id', name='unique_user_vote'),
    )

    def __init__(self, **kwargs):
        super(DecisionModel, self).__init__(**kwargs)

    @classmethod
    def add_decision(cls, vote, user, choice, comment):
        new_entry = DecisionModel()
        new_entry.vote = vote
        new_entry.user = user
        new_entry.choice = choice
        new_entry.comment = comment

        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def update_user_decision(cls, decision, choice, comment):
        decision.choice = choice
        decision.comment = comment
        db.session.commit()