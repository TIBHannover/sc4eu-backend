from flask.views import MethodView
from flask import jsonify, request

from extensions import db
from models import UserModel, CommentModel
from models.enums.vote_status import VoteStatus
from models.vote_model import VoteModel


class CreateNewVote(MethodView):
    def post(self, term_uuid):
        reqargs = request.get_json()

        assignee = UserModel.query.filter_by(display_name=reqargs.get("assignee")).first()
        experts = UserModel.getAllUsers()
        vote_type = reqargs.get("type")
        vote_reason = reqargs.get("reason")

        vote = VoteModel.initiate_new_vote(term_uuid, assignee, experts, vote_type, vote_reason)

        if not vote:
            return jsonify({"result": False, "message": "Vote already exists, Please use any other name"})

        return jsonify(
            {
                "result": True,
                "creation": 'successful',
                "Find new vote under: ": str(vote.uuid)
            })


class GetVotes(MethodView):
    def get(self, term_uuid, _vote_uuid):
        def execute():
            votes = VoteModel.get_votes().all()
            if votes:
                all_votes = [{"uuid": str(vote.uuid),
                              "term_uuid": str(term_uuid),
                              "status": vote.status.value,
                              "assignee": vote.user.display_name,
                              "type": vote.type.value,
                              "decisions": [{
                                  "vote_id": decision.vote_id,
                                  "user_name": decision.user.display_name,
                                  "comment": decision.comment,
                                  "choice": decision.choice,
                              } for decision in vote.decisions]
                              }
                             for vote in votes]
                return jsonify(all_votes)
            else:
                return jsonify({'error': "Something went wrong"})

        return execute()


class GetTermVote(MethodView):
    def get(self, term_uuid):
        def execute():
            if term_uuid:
                votes_query = VoteModel.get_all_votes_for_term_uuid(term_uuid)
                if votes_query:
                    status = request.args.get("status")
                    if status:
                        votes_query = votes_query.filter_by(status=VoteStatus(status))

                    votes = votes_query.all()

                    result = [{"uuid": str(vote.uuid),
                               "term_uuid": str(term_uuid),
                               "status": vote.status.value,
                               "assignee": vote.user.display_name,
                               "type": vote.type.value,
                               "reason": vote.reason,
                               "created_at": vote.created_at,
                               "decisions": [{
                                   "vote_id": decision.vote_id,
                                   "user_name": decision.user.display_name,
                                   "comment": decision.comment,
                                   "choice": decision.choice,
                                   "updated_at": decision.updated_at
                               } for decision in vote.decisions],
                               "discussion": {
                                   "comments": [{
                                       "id": comment.id,
                                       "user_id": comment.user_id,
                                       "user_name": comment.user.display_name if comment.user else None,
                                       "text": comment.text,
                                       "created_at": comment.created_at.isoformat() if comment.created_at else None
                                   } for comment in vote.discussion.comments.all()]
                               } if vote.discussion else None
                               }
                              for vote in votes]
                    return jsonify(result)
                else:
                    return jsonify({'error': "No votes found"})

        return execute()


class GetTermsWithActiveVotes(MethodView):
    def get(self):
        def execute():
            status = VoteStatus(request.args.get("status"))
            votes = VoteModel.get_votes().filter_by(status=status).all()
            result = {}
            for vote in votes:
                result.setdefault(str(vote.term_uuid), []).append(str(vote.uuid))
            return jsonify(result)

        return execute()


class UpdateVoteDecision(MethodView):
    def put(self, term_uuid, vote_uuid):
        reqargs = request.get_json()

        user = UserModel.query.filter_by(display_name=reqargs.get("user")).first()
        choice = reqargs["choice"]
        comment = reqargs["comment"]

        return jsonify(VoteModel.update_vote_decision(vote_uuid, user, choice, comment))


class AddNewComment(MethodView):
    def post(self, _term_uuid, vote_uuid):
        reqargs = request.get_json()

        user_uuid = reqargs["user_uuid"]
        text = reqargs["text"]

        return jsonify(VoteModel.add_new_comment(vote_uuid, user_uuid, text))


class GetDiscussion(MethodView):
    def get(self, _term_uuid, vote_uuid):
        vote = VoteModel.get_vote_by_uuid(vote_uuid)
        if vote:
            return jsonify({"discussion": vote.discussion.to_dict()})

class PostNewComments(MethodView):
    def post(self, term_uuid, vote_uuid):
        reqargs = request.get_json()
        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()
        user = UserModel.query.filter_by(display_name=reqargs.get("user")).first()

        new_comment = CommentModel.create_new_comment(vote.discussion, user, reqargs.get['text'])
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({
            "id": new_comment.id,
            "user_name": user['display_name'],
            "text": new_comment.text,
            "created_at": new_comment.created_at.isoformat()
        }), 201


class GetComments(MethodView):
    def get(self, term_uuid, vote_uuid):
        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()

        if not vote.discussion:
            return jsonify({"comments": []})

        comments = vote.discussion.comments.order_by(CommentModel.created_at.asc()).all()

        return jsonify({
            "comments": [{
                "id": c.id,
                "user_id": c.user_id,
                "user_name": c.user.display_name,
                "text": c.text,
                "created_at": c.created_at.isoformat()
            } for c in comments]
        })

class ManualVoteClose(MethodView):
    def put(self, term_uuid, vote_uuid):
        vote = VoteModel.query.filter_by(uuid=vote_uuid).first_or_404()
        print(vote)
        if not vote:
            return jsonify({'error': "No vote found"})
        return jsonify(VoteModel.admin_close_vote(vote))
