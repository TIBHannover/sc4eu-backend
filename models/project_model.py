from extensions import db
from uuid import uuid4

from sqlalchemy import func

from ._base import ModelMixin


class ProjectModel(db.Model, ModelMixin):
    __tablename__ = 'projects_table'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', db.String)
    name = db.Column('project_name', db.String)
    description = db.Column('project_description', db.String)
    access_type = db.Column('project_accesstype', db.String)
    created_by = db.Column('created_by', db.String)

    # Relationships
    ontologies = db.relationship('OntologyIndexingModel', secondary='sc3_project_ontologies',
                                 backref=db.backref('projects_table', lazy='dynamic'))

    def __init__(self, name, uuid, description, access_type, created_by):
        self.name = name
        self.uuid = uuid
        self.description = description
        self.access_type = access_type
        self.created_by = created_by

    @classmethod
    def create_new_project(cls, name, description, access_type, created_by):

        if cls.is_project_name_exists(name):
            return None
        uuid_entry = uuid4()
        new_entry = ProjectModel(name=name, uuid=uuid_entry, description=description, access_type=access_type,
                                 created_by=created_by)
        # saving entry
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id

    @classmethod
    def edit_project(cls, uuid, name, description, access_type):
        project_to_update_exists = db.session.query(ProjectModel).filter_by(
                    uuid=uuid).first() is not None

        if project_to_update_exists:
            project_to_update = db.session.query(ProjectModel).filter_by(uuid=uuid).first()
            project_to_update.name = name
            project_to_update.description = description
            project_to_update.access_type = access_type

            db.session.commit()

    @classmethod
    def delete_project(cls, project_id):
        print("CALLED TO DELETE project", flush=True)
        # Delete from DB
        project_to_delete_exists = db.session.query(ProjectModel.uuid).filter_by(
            uuid=project_id).first() is not None
        print("ProjectModel.delete_project WE are here>>>", project_to_delete_exists, flush=True)

        if project_to_delete_exists:
            # would remove it from index
            to_delete_entry = db.session.query(ProjectModel).filter_by(uuid=project_id).first()
            print(to_delete_entry, flush=True)
            db.session.delete(to_delete_entry)
            db.session.commit()

    @classmethod
    def get_all_projects(cls):
        return ProjectModel.query.order_by(ProjectModel.created_at).all()

    @classmethod
    def get_project_by_name(cls, project_name):
        return ProjectModel.query.filter_by(name=project_name).first()

    @classmethod
    def get_project_by_id(cls, project_id):
        return ProjectModel.query.filter_by(id=project_id).first()

    @classmethod
    def get_project_detail_by_id(cls, project_id):
        project = ProjectModel.query.filter_by(id=project_id).first()
        if project:
            projectDetailObject = {"uuid": project.uuid, "name": project.name, "description": project.description,
                                   "accessType": project.access_type, "createdBy": project.created_by}
            return projectDetailObject
        return None

    @classmethod
    def get_project_id_for_uuid(cls, uuid):
        project = db.session.query(ProjectModel).filter_by(uuid=uuid).first()
        if project is not None:
            return project.id
        return None

    @classmethod
    def initializeDefaultProject(cls):
        # test with example data first.
        project_name = "Default"

        does_exist = db.session.query(ProjectModel.name).filter_by(
            name=project_name).first() is not None

        if does_exist:
            print("Project already exists: " + project_name)
        else:
            cls.create_new_project(name=project_name, description="Default Project", access_type="Public",
                                   created_by="System Admin")

    @classmethod
    def is_project_name_exists(cls, project_name):
        does_project_name_exist = db.session.query(ProjectModel).filter(func.lower(ProjectModel.name) == project_name.lower()).first() is not None

        if does_project_name_exist:
            return True

