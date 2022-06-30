from extensions import db
from uuid import uuid4
from ._base import ModelMixin


class ProjectModel(db.Model, ModelMixin):
    __tablename__ = 'projects_table'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', db.String)
    name = db.Column('project_name', db.String)
    description = db.Column('project_description', db.String)
    created_by = db.Column('created_by', db.String)

    # Relationships
    ontologies = db.relationship('OntologyIndexingModel', secondary='sc3_project_ontologies',
                            backref=db.backref('projects_table', lazy='dynamic'))

    def __init__(self, name, uuid, description, created_by):
        self.name = name
        self.uuid = uuid
        self.description = description
        self.created_by = created_by

    @classmethod
    def create_new_project(cls, name, description, created_by):
        uuid_entry = uuid4()

        new_entry = ProjectModel(name=name, uuid=uuid_entry, description=description, created_by=created_by)
        # saving entry
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def delete_project(cls, project_id):
        print("CALLED TO DELETE project", flush=True )
        # Delete from DB
        project_to_delete_exists =db.session.query(ProjectModel.uuid).filter_by(
            uuid=project_id).first() is not None
        print("ProjectModel.delete_project WE are here>>>", project_to_delete_exists, flush=True)

        if project_to_delete_exists:
            # would remove it from index
            to_delete_entry=db.session.query(ProjectModel).filter_by(uuid=project_id).first()
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
    def get_project_id_for_uuid(cls, uuid):
        project = db.session.query(ProjectModel).filter_by(uuid=uuid).first()
        return project.id

    @classmethod
    def initializeDefaultProject(cls):
        # test with example data first.
        project_name = "Default"

        does_exist = db.session.query(ProjectModel.name).filter_by(
            name=project_name).first() is not None

        if does_exist:
            print("Project already exists: " + project_name)
        else:
            cls.create_new_project(name=project_name, description="Default Project", created_by="System Admin")



