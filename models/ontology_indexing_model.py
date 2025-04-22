from extensions import db
from uuid import uuid4

from flask import jsonify
from sqlalchemy import func

from ._base import ModelMixin
from .ontology_archive_model import OntologyArchiveModel
from .project_model import ProjectModel


class OntologyIndexingModel(db.Model, ModelMixin):
    __tablename__ = 'ontology_indexing_table'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', db.String)
    name = db.Column('ontology_name', db.String)
    lookup_type = db.Column('ontology_lookup_type', db.String)
    access_type = db.Column('ontology_access_type', db.String)
    lookup_path = db.Column('ontology_lookup_path', db.String)
    description = db.Column('ontology_description', db.String)
    project_id = db.Column('project_id', db.String)

    def __init__(self, name, lookup_type, access_type, lookup_path, uuid, description, project_id):
        self.name = name
        self.lookup_type = lookup_type
        self.access_type = access_type
        self.lookup_path = lookup_path
        self.uuid = uuid
        self.description = description
        self.project_id = project_id

    @classmethod
    def integrate_new_ontology(cls, name, lookup_type, access_type, path_to_data, description, content, project_id,
                               ontology_git_data):

        if cls.is_ontology_already_uploaded(name, project_id):
            return None
        uuid_entry = uuid4()

        new_entry = OntologyIndexingModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                          lookup_path=path_to_data, uuid=uuid_entry, description=description,
                                          project_id=project_id)

        OntologyArchiveModel.create_new_ontology_data_entry(name=name, lookup_type=lookup_type, access_type=access_type,
                                                            path_to_data=path_to_data, uuid_entry=uuid_entry,
                                                            content=content, ontology_git_data=ontology_git_data)

        # saving entry
        db.session.add(new_entry)
        db.session.commit()

        return True
    
    
    @classmethod
    def update_existing_ontology(cls, name, lookup_type, access_type, path_to_data, description, content, project_id, ontology_id,
                               ontology_git_data):

        ontology = cls.get_ontology_if_exists(name, project_id)
        if ontology is not None:
            # If an ontology with the same name is already uploaded for the project
            if ontology.uuid == ontology_id:
                # If the UUIDs are the same, it means it's the same ontology
                #                 

                # Update the existing ontology entry
                ontology.name = name
                ontology.lookup_type = lookup_type
                ontology.access_type = access_type
                ontology.lookup_path = path_to_data
                ontology.description = description
                ontology.project_id = project_id
                ontology.uuid = ontology_id
                # Update the ontology archive entry
                updated_ontology = OntologyArchiveModel.update_existing_ontology_data(ontology_id, content, ontology_git_data)
                if updated_ontology is None:
                    # If the ontology with the given ID does not exist, return None
                    return None
                return ontology
            else:       
                # If the UUIDs are different, it means it's a different ontology
                # You can choose to either update the existing one or create a new one
                # For now, let's just return False
                return False
        else:
            return None

    @classmethod
    def delete_ontology_index(cls, ontology_id):
        # Delete from OntologyIndexingModel
        # Delete from OntologyArchiveModel
        # Delete from DB
        ontology_to_delete_exists = db.session.query(OntologyIndexingModel.uuid).filter_by(
            uuid=ontology_id).first() is not None

        if ontology_to_delete_exists:
            # would remove it from index
            to_delete_entry = db.session.query(OntologyIndexingModel).filter_by(uuid=ontology_id).first()
            db.session.delete(to_delete_entry)
            db.session.commit()
            OntologyArchiveModel.delete_ontology_byID(ontology_id)

    #         ontology_to_delete.delete()
    #         db.session.delete(ontology_to_delete)
    #         db.session.commit()
    #         ontology_to_delete.delete()

    @classmethod
    def get_ontology_index(cls, project_id):
        # TODO: this should return Ontologies only for a give project
        # if project_id == "None":
        #     return False
        return OntologyIndexingModel.query.filter_by(project_id=project_id).order_by(
            OntologyIndexingModel.created_at.desc()).all()

        #return OntologyIndexingModel.query.order_by(OntologyIndexingModel.created_at.desc()).all()

    @classmethod
    def initializeDefaultData(cls):
        # test with example data first.
        ontology_name = "EXAMPLE"
        results = open("defaultData/example.ttl", encoding="utf8", mode='r')
        data = results.read()
        results.close()

        lookup_type = 'local'
        access_type = 'public'
        lookup_path = 'internal'
        ontology_git_data = 'none'
        project_id = ProjectModel.get_project_by_name("Default").uuid
        does_exist = db.session.query(OntologyIndexingModel.name).filter_by(
            name=ontology_name).first() is not None

        if does_exist:
            print("Ontology already exists: " + ontology_name)
        else:
            cls.integrate_new_ontology(name=ontology_name, lookup_type=lookup_type, access_type=access_type,
                                       path_to_data=lookup_path, description="EXAMPLE", content=data,
                                       project_id=project_id, ontology_git_data=ontology_git_data)

        # ######### UPLOADING DIGITAL REFERENCE
        ontology_name = "Digital Reference"
        results = open("defaultData/DigitalReference.ttl", encoding="utf8", mode='r')
        data = results.read()
        results.close()
        does_exist = db.session.query(OntologyIndexingModel.name).filter_by(
            name=ontology_name).first() is not None
        if does_exist:
            print("Ontology already exists: " + ontology_name)
        else:
            cls.integrate_new_ontology(name=ontology_name, lookup_type=lookup_type, access_type=access_type,
                                       path_to_data=lookup_path, description="DIGITAL REFERENCE TEST", content=data,
                                       project_id=project_id, ontology_git_data=ontology_git_data)

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
                                       path_to_data=lookup_path, description="Advanced Example Ontology", content=data,
                                       project_id=project_id, ontology_git_data=ontology_git_data)

    @classmethod
    def is_ontology_already_uploaded(cls, name, project_id):
        # Check if ontology with same name is already uploaded for the project
        project_id_ontologies = db.session.query(OntologyIndexingModel).filter_by(project_id=project_id).all()

        for ontology in project_id_ontologies:
            if ontology.name.lower() == name.lower():
                # If an ontology with the same name is already uploaded for the project
                return True
            
    @classmethod
    def get_ontology_if_exists(cls, name, project_id):
        # Check if ontology with same name is already uploaded for the project
        project_id_ontologies = db.session.query(OntologyIndexingModel).filter_by(project_id=project_id).all()

        for ontology in project_id_ontologies:
            if ontology.name.lower() == name.lower():
                # If an ontology with the same name is already uploaded for the project
                return ontology
            
        return None
    
    @classmethod
    def get_ontology_by_id(cls, ontology_id):
        # Check if ontology with same name is already uploaded for the project
        ontology = db.session.query(OntologyIndexingModel).filter_by(uuid=ontology_id).first()
        return ontology
    
    @classmethod
    def get_ontology_by_name(cls, name):
        # Check if ontology with same name is already uploaded for the project
        ontology = db.session.query(OntologyIndexingModel).filter_by(name=name).first()
        return ontology    