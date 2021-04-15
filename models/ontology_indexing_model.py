from extensions import db
from uuid import uuid4
from ._base import ModelMixin
from .ontology_archive_model import OntologyArchiveModel


class OntologyIndexingModel(db.Model, ModelMixin):
    __tablename__ = "ontology_indexing_table"

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', db.String)
    name = db.Column('ontology_name', db.String)
    lookup_type = db.Column('ontology_lookup_type', db.String)
    access_type = db.Column('ontology_access_type', db.String)
    lookup_path = db.Column('ontology_lookup_path', db.String)
    description = db.Column('ontology_description', db.String)

    def __init__(self, name, lookup_type, access_type, lookup_path, uuid, description):
        self.name = name
        self.lookup_type = lookup_type
        self.access_type = access_type
        self.lookup_path = lookup_path
        self.uuid = uuid
        self.description = description

    @classmethod
    def integrate_new_ontology(cls, name, lookup_type, access_type, path_to_data, description, content):
        uuid_entry = uuid4()

        new_entry = OntologyIndexingModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                          lookup_path=path_to_data, uuid=uuid_entry, description=description)

        OntologyArchiveModel.create_new_ontology_data_entry(name=name, lookup_type=lookup_type, access_type=access_type,
                                                            path_to_data=path_to_data, uuid_entry=uuid_entry,
                                                            content=content)

        # saving entry
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def get_ontology_index(cls):
        return OntologyIndexingModel.query.order_by(OntologyIndexingModel.created_at.desc()).all()
