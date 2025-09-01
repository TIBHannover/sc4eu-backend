from extensions import db
from . import UserModel, DecisionModel, CommentModel
from ._base import ModelMixin
from sqlalchemy.dialects.postgresql.base import UUID
from uuid import uuid4

from .dicsussion_model import DiscussionModel
from .enums.vote_status import VoteStatus
from .enums.vote_type import VoteType


class VoteModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_vote_model'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', UUID(as_uuid=True), unique=True, default=uuid4)
    term_uuid = db.Column('term_uuid', UUID(as_uuid=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('sc3_user_model.hash_id'), nullable=False)

    status = db.Column(db.Enum(VoteStatus), nullable=False)
    type = db.Column(db.Enum(VoteType), nullable=False)
    reason = db.Column(db.String, nullable=True)

    user = db.relationship('UserModel', back_populates='votes')
    decisions = db.relationship('DecisionModel', back_populates='vote', lazy="dynamic")
    discussion = db.relationship('DiscussionModel', back_populates='vote', uselist=False)

    def __init__(self, **kwargs):
        super(VoteModel, self).__init__(**kwargs)

    @classmethod
    def initiate_new_vote(cls, term_uuid, assignee, users, vote_type, vote_reason):
        new_entry = VoteModel()
        new_entry.type = VoteType[vote_type]
        new_entry.reason = vote_reason
        new_entry.term_uuid = term_uuid
        new_entry.status = VoteStatus.UNDER_AGREEMENT
        new_entry.discussion = DiscussionModel.default_discussion(new_entry)
        new_entry.user = assignee
        new_entry.decisions = [DecisionModel.default_for_user(user) for user in users]

        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @classmethod
    def get_votes(cls):
        return VoteModel.query.order_by(VoteModel.created_at.desc())

    @classmethod
    def get_vote_by_uuid(cls, vote_uuid):
        return VoteModel.query.filter_by(uuid=vote_uuid).first()

    @classmethod
    def get_all_votes_for_term_uuid(cls, term_uuid):
        votes = cls.get_votes().all()
        if votes:
            return cls.query.filter_by(term_uuid=term_uuid)

    @classmethod
    def get_active_vote_for_term_uuid(cls, term_uuid):
        votes = cls.get_all_votes_for_term_uuid(term_uuid)
        if votes:
            return cls.query.filter_by(status=VoteStatus.UNDER_AGREEMENT).first()

    @classmethod
    def update_vote(cls, vote, **fields_to_update):
        for key, value in fields_to_update.items():
            if hasattr(vote, key):
                setattr(vote, key, value)
            else:
                return {"error": f"Vote does not have an attribute: {key}"}

        db.session.commit()
        return {"success": f"Vote {vote.uuid} updated"}

    @classmethod
    def admin_close_vote(cls, vote):
        return VoteModel.update_vote(vote, status=VoteStatus.CLOSED)

    @classmethod
    def update_vote_decision(cls, vote_uuid, user, choice, comment):
        vote = VoteModel.get_vote_by_uuid(vote_uuid)
        if vote:
            # user_id = UserModel.get_user_id_for_uuid(user_uuid)
            decision = vote.decisions.filter_by(user_id=user.id).first()
            if decision:
                DecisionModel.update_user_decision(decision, choice, comment)
                return {"success": f"Decision for {vote.uuid} updated with {user.id} choice"}
            return {"error": "There is no such user in this vote's decision"}

    @classmethod
    def add_new_comment(cls, vote_uuid, user_id, text):
        vote = VoteModel.get_vote_by_uuid(vote_uuid)
        if vote:
            new_comment = CommentModel.create_new_comment(vote.id, user_id, text)
            db.session.add(new_comment)
            db.session.commit()

            return {"success": "New comment added"}



