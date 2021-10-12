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
    def delete_ontology_index(cls, ontology_id):
        print("CALLED TO DELETE", flush=True )
        # Delete from OntologyIndexingModel
        # Delete from OntologyArchiveModel
        # Delete from DB
        ontology_to_delete_exists =db.session.query(OntologyIndexingModel.uuid).filter_by(
            uuid=ontology_id).first() is not None
        print("INDEX MODEL WE are here>>>", ontology_to_delete_exists, flush=True)

        if ontology_to_delete_exists:
            # would remove it from index
            to_delete_entry=db.session.query(OntologyIndexingModel).filter_by(uuid=ontology_id).first()
            print(to_delete_entry, flush=True)
            db.session.delete(to_delete_entry)
            db.session.commit()
            OntologyArchiveModel.delete_ontology_byID(ontology_id)
    #         ontology_to_delete.delete()
    #         db.session.delete(ontology_to_delete)
    #         db.session.commit()
    #         ontology_to_delete.delete()

    @classmethod
    def get_ontology_index(cls):
        return OntologyIndexingModel.query.order_by(OntologyIndexingModel.created_at.desc()).all()

    @classmethod
    def initializeDefaultData(cls):
        # test with example data first.
        ontology_name = "EXAMPLE"
        results = open("defaultData/example.ttl",  encoding="utf8", mode='r')
        data = results.read()
        results.close()

        lookup_type = 'local'
        access_type = 'public'
        lookup_path = 'internal'
        does_exist = db.session.query(OntologyIndexingModel.name).filter_by(
            name=ontology_name).first() is not None

        if does_exist:
            print("Ontology already exists: " + ontology_name)
        else:
            cls.integrate_new_ontology(name=ontology_name, lookup_type=lookup_type, access_type=access_type,
                                       path_to_data=lookup_path, description="EXAMPLE", content=data)

        # ######### UPLOADING DIGITAL REFERENCE
        ontology_name = "DR-TEST"
        results = open("defaultData/DigitalReference.ttl", encoding="utf8", mode='r')
        data = results.read()
        results.close()
        does_exist = db.session.query(OntologyIndexingModel.name).filter_by(
            name=ontology_name).first() is not None
        if does_exist:
            print("Ontology already exists: " + ontology_name)
        else:
            cls.integrate_new_ontology(name=ontology_name, lookup_type=lookup_type, access_type=access_type,
                                       path_to_data=lookup_path, description="DIGITAL REFERENCE TEST", content=data)


        # ######### UPLOADING DIGITAL REFERENCE
        ontology_name = "Advanced Example"
        results = open("defaultData/advanceExample.ttl", encoding="utf8", mode='r')
        data = results.read()
        results.close()
        does_exist = db.session.query(OntologyIndexingModel.name).filter_by(
            name=ontology_name).first() is not None
        if does_exist:
            print("Ontology already exists: " + ontology_name)
        else:
            cls.integrate_new_ontology(name=ontology_name, lookup_type=lookup_type, access_type=access_type,
                                       path_to_data=lookup_path, description="Advanced Example Ontology", content=data)

