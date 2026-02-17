from extensions import db
from . import UserModel, DecisionModel, CommentModel
from ._base import ModelMixin
from sqlalchemy.dialects.postgresql.base import UUID
from uuid import uuid4
from sqlalchemy import select, func, desc
from .dicsussion_model import DiscussionModel
from .enums.decision_choice import DecisionChoice
from .enums.vote_status import VoteStatus
from .enums.vote_type import VoteType
from datetime import datetime, timedelta

class VoteModel(db.Model, ModelMixin):
    __tablename__ = "sc3_vote_model"

    id = db.Column("hash_id", db.Integer, primary_key=True, unique=True)
    uuid = db.Column("uuid", UUID(as_uuid=True), unique=True, default=uuid4)
    term_uuid = db.Column("term_uuid", UUID(as_uuid=True), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("sc3_user_model.hash_id"), nullable=False
    )

    status = db.Column(db.Enum(VoteStatus), nullable=False)
    type = db.Column(db.Enum(VoteType), nullable=False)
    reason = db.Column(db.String, nullable=True)

    user = db.relationship("UserModel", back_populates="votes")
    decisions = db.relationship(
        "DecisionModel",
        back_populates="vote",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    discussion = db.relationship(
        "DiscussionModel",
        back_populates="vote",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        super(VoteModel, self).__init__(**kwargs)

    @classmethod
    def initiate_new_vote(cls, term_uuid, assignee, vote_type, vote_reason):
        new_entry = VoteModel()
        new_entry.type = VoteType[vote_type]
        new_entry.reason = vote_reason
        new_entry.term_uuid = term_uuid
        new_entry.status = VoteStatus.UNDER_AGREEMENT
        new_entry.discussion = DiscussionModel.default_discussion(new_entry)
        new_entry.user = assignee
        new_entry.decisions = []

        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @classmethod
    def get_votes(cls):
        return cls.query.order_by(VoteModel.created_at.desc())

    @classmethod
    def get_vote_by_uuid(cls, vote_uuid):
        return cls.query.filter_by(uuid=vote_uuid).first()

    @classmethod
    def get_all_votes_for_term_uuid(cls, term_uuid):
        return cls.query.filter_by(term_uuid=term_uuid)

    @classmethod
    def get_active_vote_for_term_uuid(cls, term_uuid):
        return cls.query.filter_by(
            term_uuid=term_uuid, status=VoteStatus.UNDER_AGREEMENT
        ).first()

    @classmethod
    def get_last_non_active_consensus_for_term_uuid(cls, term_uuid):
        return (
            cls.query.filter(
                cls.term_uuid == term_uuid,
                cls.status.notin_(
                    [VoteStatus.UNDER_AGREEMENT, VoteStatus.UNDER_REVISION]
                ),
            )
            .order_by(cls.created_at.desc())
            .first()
        )

    # initially intended to update all term field, now used only for term's status
    # if in a future an idea of updating other term fields arises, return must be updated
    # for now will only be used with term's status
    @classmethod
    def update_vote(cls, vote, **fields_to_update):
        for key, value in fields_to_update.items():
            if hasattr(vote, key):
                setattr(vote, key, value)
            else:
                return {"error": f"Vote does not have an attribute: {key}"}

        db.session.commit()
        return {"success": f"Vote {vote.uuid} updated", "status": vote.status.value}

    @classmethod
    def admin_close_vote(cls, vote):
        approved = sum(d.choice == DecisionChoice.APPROVE.value for d in vote.decisions)
        rejected = sum(d.choice == DecisionChoice.REJECT.value for d in vote.decisions)
        total = approved + rejected
        threshold = 3

        if total == 0:
            return cls.update_vote(vote, status=VoteStatus.CLOSED)

        def approved_type_status():
            if vote.type == VoteType.ACCEPT:
                return VoteStatus.ACCEPT
            else:
                return VoteStatus.NOT_ACCEPT

        if approved >= threshold > rejected:
            return cls.update_vote(vote, status=approved_type_status())
        if rejected >= threshold > approved:
            return cls.update_vote(vote, status=VoteStatus.DRAFT)

        majority = total * 2 / 3
        if approved > majority:
            status = approved_type_status()
        elif rejected > majority:
            status = VoteStatus.DRAFT
        else:
            status = VoteStatus.CLOSED

        return cls.update_vote(vote, status=status)

    @classmethod
    def update_vote_decision(cls, vote_uuid, user, choice, comment):
        vote = cls.get_vote_by_uuid(vote_uuid)
        if vote:
            decision = vote.decisions.filter_by(user_id=user.id).first()
            if decision:
                DecisionModel.update_user_decision(decision, choice, comment)
                return {
                    "success": f"Decision for {vote.uuid} updated with {user.id} choice"
                }
            else:
                DecisionModel.add_decision(vote, user, choice, comment)
            return {"error": "There is no such user in this vote's decision"}

    @classmethod
    def add_new_comment(cls, vote_uuid, user_id, text):
        vote = cls.get_vote_by_uuid(vote_uuid)
        if vote:
            new_comment = CommentModel.create_new_comment(vote.id, user_id, text)
            db.session.add(new_comment)
            db.session.commit()

            return {"success": "New comment added"}

    @classmethod
    def consensus_with_most_choices_in_week(cls):
        week_delta = datetime.now() - timedelta(days=700)

        choices_counts = (
            select(
                cls.uuid.label("vote_uuid"),
                cls.term_uuid,
                func.count(DecisionModel.id).label("choice_count"),
            )
            .join(cls.decisions)
            .where(cls.status == VoteStatus.UNDER_AGREEMENT,
                   DecisionModel.created_at >= week_delta)
            .group_by(cls.uuid, cls.term_uuid)
            .order_by(desc("choice_count"))
        )

        return db.session.execute(choices_counts).all()
