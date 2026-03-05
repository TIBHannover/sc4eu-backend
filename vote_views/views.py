from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from services.notifications import notify_new_vote
from models import UserModel
from models.enums.vote_status import VoteStatus
from models.vote_model import VoteModel
from models.enums.decision_choice import DecisionChoice
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
from extensions import get_db

term_router = APIRouter(prefix="/terms", tags=["terms"])
vote_router = APIRouter(prefix="/votes", tags=["votes"])
term_vote_router = APIRouter(prefix="/terms/{term_uuid}/votes", tags=["term_votes"])

class Decision(BaseModel):
    vote_id: int
    user_id: int
    user_name: str
    comment: Optional[str]
    choice: Optional[str]
    created_at: datetime
    updated_at: datetime


class Comment(BaseModel):
    discussion_id: int
    user_id: int
    text: str


class Discussion(BaseModel):
    vote_id: int
    comments: Optional[List[Comment]]


class Vote(BaseModel):
    uuid: UUID
    term_uuid: UUID
    user_id: int
    assignee: str
    status: str
    type: str
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    decisions: List[Decision]
    discussion: Optional[Discussion]
    model_config = ConfigDict(from_attributes=True)


class NonActiveConsensus(BaseModel):
    type: str
    status: str
    assignee: str
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    decisions: List[Decision]
    approved_decisions: int
    rejected_decisions: int
    total_decisions: int
    model_config = ConfigDict(from_attributes=True)

class ConsensusOfWeek(BaseModel):
    term_uuid: UUID
    vote_uuid: UUID
    choice_count: int

class VoteUpdateRequest(BaseModel):
    user_name: str
    choice: str
    comment: Optional[str] = None


class NewVoteRequest(BaseModel):
    assignee: str
    type: str
    reason: Optional[str] = None


@term_router.get("/consensus/{term_uuid}", response_model=Optional[NonActiveConsensus])
async def get_consensus_term_uuid(
    term_uuid: str = Path(title="Term universally unique identifier (UUID)"),
    db_session: Session = Depends(get_db),
):

    if not term_uuid:
        raise HTTPException(status_code=400, detail="Term UUID is required")
    last_consensus = (
        db_session.query(VoteModel)
        .filter(
            VoteModel.term_uuid == term_uuid,
            VoteModel.status.notin_(
                [VoteStatus.UNDER_AGREEMENT, VoteStatus.UNDER_REVISION]
            ),
        )
        .order_by(VoteModel.created_at.desc())
        .first()
    )

    logger.error(f"last consensus: {last_consensus}")
    if not last_consensus:
        return None

    return last_consensus


@term_router.get("/ofTheWeek", response_model=ConsensusOfWeek)
async def get_consensus_of_the_week(
    db_session: Session = Depends(get_db),
):

    choices = VoteModel.consensus_with_most_choices_in_week(db_session)

    if not choices:
        return None

    return choices[0]


@vote_router.get("", response_model=List[Vote])
async def get_all_votes(
    status: Optional[str] = Query(None, description="Filter by status"),
    db_session: Session = Depends(get_db),
):
    votes_query = VoteModel.get_votes_fastapi(db_session)

    if status:
        if not VoteStatus.is_valid(status):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Expected one of: {VoteStatus.to_string()}",
            )
        votes_query = votes_query.filter_by(status=VoteStatus(status))

    return votes_query.order_by(VoteModel.created_at.desc()).all()


@term_vote_router.get("", response_model=Optional[List[Vote]])
async def get_votes(
    term_uuid: Optional[str] = Path(title="Term universally unique identifier (UUID)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db_session: Session = Depends(get_db),
):
    votes_query = VoteModel.get_all_votes_for_term_uuid_fastapi(db_session, term_uuid)
    if not votes_query:
        return []

    if not VoteStatus.is_valid(status):
        valid_choices = VoteStatus.to_string()
        return HTTPException(
            status_code=400,
            detail=f"Invalid status '{status}'. Expected one of: {valid_choices}",
        )

    logger.error(f"Status {status}")
    votes = (
        votes_query.filter_by(status=VoteStatus(status))
        .order_by(VoteModel.created_at.desc())
        .all()
    )
    logger.error(f"Votes after filtering {votes}")
    return votes


@term_vote_router.post("")
async def create_new_vote(
    term_uuid: str = Path(title="Term universally unique identifier (UUID)"),
    payload: NewVoteRequest = Body(
        description="Body with choice, user_name and comment (optional)"
    ),
    db_session: Session = Depends(get_db),
):

    if not payload.type or not payload.assignee:
        raise HTTPException(
            status_code=400,
            detail="Vote type and assignee is required",
        )

    user = db_session.query(UserModel).filter_by(display_name=payload.assignee).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail=f"Assignee with username {payload.assignee} not found",
        )

    vote = VoteModel.initiate_new_vote_fastapi(
        db_session, term_uuid, user, payload.type, payload.reason
    )

    if not vote:
        raise HTTPException(
            status_code=400,
            detail=f"There is already an ongoing consensus for {term_uuid} term",
        )

    return JSONResponse(content=str(vote.uuid), status_code=201)


@term_vote_router.put("/{vote_uuid}/close")
async def close_vote(
    vote_uuid: str = Path(title="Vote universally unique identifier (UUID)"),
    db_session: Session = Depends(get_db),
):

    vote = db_session.query(VoteModel).filter_by(uuid=vote_uuid).first()

    if not vote:
        return None

    result = VoteModel.admin_close_vote(db_session, vote)
    return result

@term_vote_router.put("/{vote_uuid}")
async def update_vote_decision(
    term_uuid: str = Path(title="Term universally unique identifier (UUID)"),
    vote_uuid: str = Path(title="Vote universally unique identifier (UUID)"),
    payload: VoteUpdateRequest = Body(
        description="Body with choice, user_name and comment (optional)"
    ),
    db_session: Session = Depends(get_db),
):
    logger.error(f"Received payload = {payload}")

    user = db_session.query(UserModel).filter_by(display_name=payload.user_name).first()
    if not user:
        raise HTTPException(
            status_code=400, detail=f"User with username {payload.user_name} not found"
        )

    if not payload.choice or not DecisionChoice.is_valid(payload.choice):
        valid_choices = DecisionChoice.to_string()
        return HTTPException(
            status_code=400,
            detail=f"Invalid choice '{payload.choice}'. Expected one of: {valid_choices}",
        )

    vote = db_session.query(VoteModel).filter_by(uuid=vote_uuid).first()

    if not vote:
        return None

    return VoteModel.update_vote_decision(
        db_session, vote_uuid, user, payload.choice, payload.comment
    )
