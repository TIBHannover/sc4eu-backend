from uuid import uuid4

from extensions import db

from .ontology_indexing_model import OntologyIndexingModel
from .ontology_archive_model import OntologyArchiveModel


class ProjectOntology(db.Model):
    __tablename__ = 'sc3_project_ontologies'
    id = db.Column(db.Integer(), primary_key=True)
    project_id = db.Column(db.Integer(), db.ForeignKey('projects_table.hash_id', ondelete='CASCADE'))
    ontology_id = db.Column(db.Integer(), db.ForeignKey('ontology_indexing_table.hash_id', ondelete='CASCADE'))


# TODO: a method here to add project ontology pairs?
