from marshmallow import Schema, fields

class CreateNewVoteParams(Schema):
    term_uuid = fields.String()
    experts = fields.List(fields.String())
    changedFields = fields.List(fields.String())
    reason = fields.String()

class GetVoteParams(Schema):
    vote_uuid = fields.String()
    token = fields.String()

class AdminCloseVoteParams(Schema):
    user_uuid = fields.String()
    vote_uuid = fields.String()
    token = fields.String()

class UpdateVoteDecisionParams(Schema):
    user_uuid = fields.String()
    choice = fields.String()
    comment = fields.String
    token = fields.String()