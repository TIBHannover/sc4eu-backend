from extensions import db
from models._base import ModelMixin
from models.enums.vote_status import VoteStatus


class DecisionModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_decision_model'

    vote_id = db.Column(db.Integer, db.ForeignKey('sc3_vote_model.hash_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sc3_user_model.hash_id'), primary_key=True)

    comment = db.Column(db.String, nullable=True)
    choice = db.Column(db.String, nullable=True)

    vote = db.relationship('VoteModel', back_populates='decisions')
    user = db.relationship('UserModel', back_populates='decisions')

    def __init__(self, **kwargs):
        super(DecisionModel, self).__init__(**kwargs)

    @classmethod
    def default_for_user(cls, user, choice=None, comment=None):
        return cls(user=user, choice=choice, comment=comment)

    @classmethod
    def update_user_decision(cls, decision, choice, comment):
        decision.choice = choice
        decision.comment = comment
        db.session.commit()

        from models import VoteModel
        vote = db.session.query(VoteModel).filter_by(id=decision.vote_id).first()
        decisions = vote.decisions.all()
        if all(decision.choice == "approved" for decision in decisions):
            vote.status = VoteStatus.APPROVED.value
            db.session.commit()