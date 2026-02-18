from flask import jsonify, request, Blueprint

from extensions import db
from models import UserModel, CommentModel
from models.enums.vote_status import VoteStatus
from models.vote_model import VoteModel
from models.enums.decision_choice import DecisionChoice

term_blueprint = Blueprint("terms", __name__, url_prefix="/terms")
vote_blueprint = Blueprint("votes", __name__, url_prefix="/terms/<string:term_uuid>/votes")

@vote_blueprint.route("", methods=["POST"])
def create_new_vote(term_uuid):
    try:
        reqargs = request.get_json()

        if not reqargs:
            return jsonify({"error": "Invalid JSON data"}), 400

        assignee = UserModel.query.filter_by(
            display_name=reqargs.get("assignee")
        ).first()
        vote_type = reqargs.get("type")
        vote_reason = reqargs.get("reason")

        if not vote_type or not vote_reason:
            return jsonify({"error": "Vote type and vote reason is required"}), 400

        if not assignee:
            return jsonify(
                {
                    "error": f"Assignee with username {reqargs.get('assignee')} not found"
                }
            ), 400

        vote = VoteModel.initiate_new_vote(
            term_uuid, assignee, vote_type, vote_reason
        )

        if not vote:
            return jsonify(
                {
                    "error": f"There is already an ongoing consensus for {term_uuid} term"
                }
            ), 400

        return jsonify({"result": True, "vote_uuid": str(vote.uuid)}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>", methods=["GET"])
def get_vote(term_uuid, _vote_uuid):
    votes = VoteModel.get_votes().all()
    if not votes:
        return jsonify([]), 200

    all_votes = [
        {
            "uuid": str(vote.uuid),
            "term_uuid": str(term_uuid),
            "status": vote.status.value,
            "assignee": vote.user.display_name,
            "type": vote.type.value,
            "decisions": [
                {
                    "vote_id": decision.vote_id,
                    "user_name": decision.user.display_name,
                    "comment": decision.comment,
                    "choice": decision.choice,
                }
                for decision in vote.decisions
            ],
        }
        for vote in votes
    ]
    return jsonify(all_votes), 200


@vote_blueprint.route("", methods=["GET"])
def get_term_votes(term_uuid):
    try:
        if not term_uuid:
            return jsonify({"error": "Term UUID is required"}), 400

        votes_query = VoteModel.get_all_votes_for_term_uuid(term_uuid)
        if not votes_query:
            return jsonify([]), 200

        status = request.args.get("status")
        if status:
            votes_query = votes_query.filter_by(status=VoteStatus(status))

        votes = votes_query.all()

        result = [
            {
                "uuid": str(vote.uuid),
                "term_uuid": str(term_uuid),
                "status": vote.status.value,
                "assignee": vote.user.display_name,
                "type": vote.type.value,
                "reason": vote.reason,
                "created_at": vote.created_at.isoformat(),
                "decisions": [
                    {
                        "vote_id": decision.vote_id,
                        "user_name": decision.user.display_name,
                        "comment": decision.comment,
                        "choice": decision.choice,
                        "created_at": decision.created_at.isoformat(),
                        "updated_at": decision.updated_at.isoformat(),
                    }
                    for decision in vote.decisions
                ],
                "discussion": {
                    "comments": [
                        {
                            "id": comment.id,
                            "user_id": comment.user_id,
                            "user_name": comment.user.display_name
                            if comment.user
                            else None,
                            "text": comment.text,
                            "created_at": comment.created_at.isoformat()
                            if comment.created_at
                            else None,
                        }
                        for comment in vote.discussion.comments.all()
                    ]
                }
                if vote.discussion
                else None,
            }
            for vote in votes
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@term_blueprint.route("", methods=["GET"])
def get_all_terms_consensuses():
    try:
        status = VoteStatus(request.args.get("status"))
        if not status:
            return jsonify({"error": "Status is required"}), 400

        votes = VoteModel.get_votes().filter_by(status=status).all()
        if not votes:
            return jsonify([]), 200

        result = [
            {
                "term_uuid": str(vote.term_uuid),
                "vote_uuid": str(vote.uuid),
                "decisions": [
                    {
                        "vote_id": decision.vote_id,
                        "user_name": decision.user.display_name,
                        "comment": decision.comment,
                        "choice": decision.choice,
                        "created_at": decision.created_at.isoformat(),
                        "updated_at": decision.updated_at.isoformat(),
                    }
                    for decision in vote.decisions
                ],
            }
            for vote in votes
        ]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@term_blueprint.route("/consensus/<string:term_uuid>", methods=["GET"])
def get_consensus_term_uuid(term_uuid):
    try:
        if not term_uuid:
            return jsonify({"error": "Term UUID is required"}), 400

        last_consensus = VoteModel.get_last_non_active_consensus_for_term_uuid(
            term_uuid
        )
        if not last_consensus:
            return jsonify({}), 200

        result = {
            "type": last_consensus.type.value,
            "status": last_consensus.status.value,
            "assignee": last_consensus.user.display_name,
            "reason": last_consensus.reason,
            "created_at": last_consensus.created_at.isoformat(),
            "decisions": [
                {
                    "user_name": decision.user.display_name,
                    "comment": decision.comment,
                    "choice": decision.choice,
                    "created_at": decision.created_at.isoformat(),
                    "updated_at": decision.updated_at.isoformat(),
                }
                for decision in last_consensus.decisions
            ],
            "approved_decisions": sum(
                d.choice == DecisionChoice.APPROVE.value
                for d in last_consensus.decisions
            ),
            "rejected_decisions": sum(
                d.choice == DecisionChoice.REJECT.value
                for d in last_consensus.decisions
            ),
            "total_decisions": last_consensus.decisions.count(),
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>", methods=["PUT"])
def update_vote_decision(term_uuid, vote_uuid):
    try:
        reqargs = request.get_json()

        if not reqargs:
            return jsonify({"error": "Invalid JSON data"}), 400

        user = UserModel.query.filter_by(display_name=reqargs.get("user")).first()
        if not user:
            return jsonify(
                {"error": f"User with username ${reqargs.get('user')} not found"}
            ), 400

        choice = reqargs["choice"]
        if choice is None or not DecisionChoice.is_valid(choice):
            return jsonify(
                {
                    "error": f"Choice is required or value is not valid. Expected one of {DecisionChoice.get_valid_choices()}"
                }
            )

        comment = reqargs["comment"]

        return jsonify(
            VoteModel.update_vote_decision(vote_uuid, user, choice, comment)
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>", methods=["POST"])
def post_comment(_term_uuid, vote_uuid):
    try:
        reqargs = request.get_json()

        if not reqargs:
            return jsonify({"error": "Invalid JSON data"}), 400

        user_uuid = reqargs["user_uuid"]
        text = reqargs["text"]

        return jsonify(VoteModel.add_new_comment(vote_uuid, user_uuid, text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>", methods=["GET"])
def get_discussion(_term_uuid, vote_uuid):
    try:
        vote = VoteModel.get_vote_by_uuid(vote_uuid)
        if not vote:
            return jsonify({}), 200
        return jsonify({"discussion": vote.discussion.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>/comments", methods=["POST"])
def post_new_comment(term_uuid, vote_uuid):
    try:
        reqargs = request.get_json()
        if not reqargs:
            return jsonify({"error": "Invalid JSON data"}), 400

        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()
        user = UserModel.query.filter_by(display_name=reqargs.get("user")).first()

        new_comment = CommentModel.create_new_comment(
            vote.discussion, user, reqargs.get["text"]
        )
        db.session.add(new_comment)
        db.session.commit()

        return jsonify(
            {
                "id": new_comment.id,
                "user_name": user["display_name"],
                "text": new_comment.text,
                "created_at": new_comment.created_at.isoformat(),
            }
        ), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>/comments", methods=["GET"])
def get_comments(term_uuid, vote_uuid):
    try:
        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()

        if not vote.discussion:
            return jsonify({"comments": []})

        comments = vote.discussion.comments.order_by(
            CommentModel.created_at.asc()
        ).all()

        return jsonify(
            {
                "comments": [
                    {
                        "id": c.id,
                        "user_id": c.user_id,
                        "user_name": c.user.display_name,
                        "text": c.text,
                        "created_at": c.created_at.isoformat(),
                    }
                    for c in comments
                ]
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vote_blueprint.route("<string:vote_uuid>/close", methods=["PUT"])
def vote_manual_close(term_uuid, vote_uuid):
    try:
        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()
        print(vote)
        if not vote:
            return jsonify({"error": "No vote found"})

        result = VoteModel.admin_close_vote(vote)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@term_blueprint.route("/ofTheWeek", methods=["GET"])
def get_consensus_of_the_week():
    try:
        choices = VoteModel.consensus_with_most_choices_in_week()

        if not choices:
            return "", 204

        most_choices_consensus = choices[0]

        return jsonify(
            {
                "vote_uuid": str(most_choices_consensus.vote_uuid),
                "term_uuid": str(most_choices_consensus.term_uuid),
                "choice_count": most_choices_consensus.choice_count,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
