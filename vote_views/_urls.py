from flask import Blueprint

from vote_views.views import (CreateNewVote, GetTermVote, UpdateVoteDecision, GetVotes, AddNewComment, GetDiscussion,
                              GetTermsWithActiveVotes, GetComments, PostNewComments, ManualVoteClose, GetTermLastConsensus, GetTermConsensusOfWeek)

term_blueprint = Blueprint('term', __name__, url_prefix='/terms')
vote_blueprint = Blueprint('vote', __name__, url_prefix='/<string:term_uuid>/votes')

term_blueprint.register_blueprint(vote_blueprint)

# --- Term ROUTES ---

term_blueprint.add_url_rule(
    '',
    view_func=GetTermsWithActiveVotes.as_view('get_terms_with_active_vote'),
    methods=['GET']
)

term_blueprint.add_url_rule(
    '/consensus/<string:term_uuid>',
    view_func=GetTermLastConsensus.as_view('get_term_last_consensus'),
    methods=['GET']
)

# --- Consensus ROUTES ---

vote_blueprint.add_url_rule(
    '',
    view_func=CreateNewVote.as_view('create_new_vote'),
    methods=['POST']
)

vote_blueprint.add_url_rule(
    '',
    view_func=GetTermVote.as_view('get_term_votes'),
    methods=['GET']
)

vote_blueprint.add_url_rule(
    '<string:vote_uuid>',
    view_func=GetVotes.as_view('get_vote'),
    methods=['GET']
)

vote_blueprint.add_url_rule(
    '<string:vote_uuid>',
    view_func=UpdateVoteDecision.as_view('update_vote_decision'),
    methods=['PUT']
)

vote_blueprint.add_url_rule(
    '<string:vote_uuid>',
    view_func=AddNewComment.as_view('new_comment'),
    methods=['POST']
)

vote_blueprint.add_url_rule(
    '<string:vote_uuid>',
    view_func=GetDiscussion.as_view('get_discussion'),
    methods=['GET']
)

vote_blueprint.add_url_rule('<string:vote_uuid>/comments', view_func=GetComments.as_view('get_comments'), methods=['GET'])

vote_blueprint.add_url_rule('<string:vote_uuid>/comments', view_func=PostNewComments.as_view('post_new_comment'), methods=['POST'])

vote_blueprint.add_url_rule('<string:vote_uuid>/close', view_func=ManualVoteClose.as_view('manual_close'), methods=['PUT'])

term_blueprint.add_url_rule('/ofTheWeek', view_func=GetTermConsensusOfWeek.as_view('of_the_week_consensus'), methods=['GET'])