from marshmallow import Schema
from webargs import fields


class UserHeaderGetParams(Schema):
    userId = fields.String()
    token = fields.String()


class ViewProfileArgs(Schema):
    userId = fields.String()
    token = fields.String()


class UserRoleArgs(Schema):
    userId = fields.String()
    userRole = fields.Integer()
    token = fields.String()


class UserProjectsGetParams(Schema):
    userId = fields.String()
    projectsId = fields.List(fields.String())
    token = fields.String()
