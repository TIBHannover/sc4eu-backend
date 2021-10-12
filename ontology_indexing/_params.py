from marshmallow import Schema
from webargs import fields


class OntologyIndexingGetParams(Schema):
    ontology_id = fields.String()


class UserHeaderGetParams(Schema):
    userId = fields.String()
    token = fields.String()


class UploadOntologyGetParams(Schema):
    userId = fields.String()
    token = fields.String()

class DeleteOntologyGetParams(Schema):
    ontology_id = fields.String()
    userId = fields.String()
    token = fields.String()