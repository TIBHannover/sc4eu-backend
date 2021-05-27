from marshmallow import Schema
from webargs import fields


class UserHeaderGetParams(Schema):
    userId = fields.String()
    token = fields.String()


class ViewProfileArgs(Schema):
    userId = fields.String()
    token = fields.String()
