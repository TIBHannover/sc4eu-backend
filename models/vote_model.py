from extensions import db
from . import DecisionModel
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

    @property
    def assignee(self) -> str:
        return self.user.display_name
    
    @property
    def approved_decisions(self) -> int:
        return sum(
            1
            for d in self.decisions.all()
            if d.choice == DecisionChoice.APPROVE.value
        )

    @property
    def rejected_decisions(self) -> int:
        return sum(
            1
            for d in self.decisions.all()
            if d.choice == DecisionChoice.REJECT.value
        )

    @property
    def total_decisions(self) -> int:
        return self.decisions.count()

    def __init__(self, **kwargs):
        super(VoteModel, self).__init__(**kwargs)

    @classmethod
    def initiate_new_vote_fastapi(cls, db_session, term_uuid, assignee, vote_type, vote_reason):
        try:
            existing_vote = VoteModel.get_active_vote_for_term_uuid_fastapi(db_session, term_uuid)
            print(existing_vote)
            if existing_vote:
                return None

            new_entry = VoteModel()
            new_entry.type = VoteType[vote_type]
            new_entry.reason = vote_reason
            new_entry.term_uuid = term_uuid
            new_entry.status = VoteStatus.UNDER_AGREEMENT
            new_entry.discussion = DiscussionModel.default_discussion(new_entry)
            new_entry.user = assignee
            new_entry.decisions = []

            print(new_entry)
            db_session.add(new_entry)
            db_session.commit()
            return new_entry
        except Exception:
            db_session.rollback()
            raise

    @classmethod
    def get_votes_fastapi(cls, db_session):
        return db_session.query(VoteModel).order_by(VoteModel.created_at.desc())

    @classmethod
    def get_vote_by_uuid_fastapi(cls, db_session, vote_uuid):
        return db_session.query(VoteModel).filter_by(uuid=vote_uuid).first()

    @classmethod
    def get_all_votes_for_term_uuid_fastapi(cls, db_session, term_uuid):
        return db_session.query(VoteModel).filter_by(term_uuid=term_uuid)

    @classmethod
    def get_active_vote_for_term_uuid_fastapi(cls, db_session, term_uuid):
        return db_session.query(VoteModel).filter_by(
            term_uuid=term_uuid, status=VoteStatus.UNDER_AGREEMENT
        ).first()

    @classmethod
    def get_last_non_active_consensus_for_term_uuid_fastapi(cls, term_uuid):
        return (
            VoteModel.query.filter(
                VoteModel.term_uuid == term_uuid,
                VoteModel.status.notin_(
                    [VoteStatus.UNDER_AGREEMENT, VoteStatus.UNDER_REVISION]
                ),
            )
            .order_by(VoteModel.created_at.desc())
            .first()
        )

    # initially intended to update all term field, now used only for term's status
    # if in a future an idea of updating other term fields arises, return must be updated
    # for now will only be used with term's status
    @classmethod
    def update_vote(cls, db_session, vote, **fields_to_update):
        for key, value in fields_to_update.items():
            if hasattr(vote, key):
                setattr(vote, key, value)
            else:
                return {"error": f"Vote does not have an attribute: {key}"}

        db_session.commit()
        return {"success": f"Vote {vote.uuid} updated", "status": vote.status.value}

    @classmethod
    def admin_close_vote(cls, db_session, vote):
        approved = sum(d.choice == DecisionChoice.APPROVE.value for d in vote.decisions)
        rejected = sum(d.choice == DecisionChoice.REJECT.value for d in vote.decisions)
        total = approved + rejected
        threshold = 4

        if total == 0:
            return VoteModel.update_vote(db_session, vote, status=VoteStatus.CLOSED)

        def approved_type_status():
            if vote.type == VoteType.ACCEPT:
                return VoteStatus.ACCEPT
            else:
                return VoteStatus.NOT_ACCEPT

        if approved >= threshold > rejected:
            return VoteModel.update_vote(db_session, vote, status=approved_type_status())
        if rejected >= threshold > approved:
            return VoteModel.update_vote(db_session, vote, status=VoteStatus.DRAFT)

        majority = total * 3 / 4
        if approved > majority:
            status = approved_type_status()
        elif rejected > majority:
            status = VoteStatus.DRAFT
        else:
            status = VoteStatus.CLOSED

        return VoteModel.update_vote(db_session, vote, status=status)

    @classmethod
    def update_vote_decision(cls, db_session, vote_uuid, user, choice, comment):
        vote = VoteModel.get_vote_by_uuid_fastapi(db_session, vote_uuid)

        if not vote:
            return {"error": f"Vote with {vote_uuid} not found"}

        decision = vote.decisions.filter_by(user_id=user.id).first()

        if decision:
            DecisionModel.update_user_decision(db_session, decision, choice, comment)
            return {
                "success": f"Decision for {vote.uuid} updated with {user.id} choice"
            }

        # If decision does not exist → create it
        DecisionModel.add_decision(db_session, vote, user, choice, comment)

        return {
            "success": f"Decision created for vote {vote.uuid} with {user.id}"
        }

    # Should have a delta equal to 7 days. Currently, has period of last year
    @classmethod
    def consensus_with_most_choices_in_week(cls, db_session):
        delta = datetime.now() - timedelta(days=365)

        choices_counts = (
            select(
                VoteModel.uuid.label("vote_uuid"),
                VoteModel.term_uuid,
                func.count(DecisionModel.id).label("choice_count"),
            )
            .join(DecisionModel)
            .where(
                VoteModel.status == VoteStatus.UNDER_AGREEMENT,
                DecisionModel.created_at >= delta,
            )
            .group_by(VoteModel.uuid, VoteModel.term_uuid)
            .order_by(desc("choice_count"))
        )

        return db_session.execute(choices_counts).all()
