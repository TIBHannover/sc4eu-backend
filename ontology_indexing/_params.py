from marshmallow import Schema
from webargs import fields


class OntologyIndexingGetParams(Schema):
    ontology_id = fields.String()
