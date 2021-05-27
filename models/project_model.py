from extensions import db
from uuid import uuid4
from ._base import ModelMixin


# Define the Role data-model
class ProjectRole(db.Model):
    __tablename__ = 'sc3ProjectModel'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, role_name):
        self.name = role_name

    @classmethod
    def role_exists(cls, role_name):
        role = db.session.query(cls).filter_by(name=role_name).first()
        if role:
            return True
        else:
            return False

    @classmethod
    def create_role(cls, role_name):
        # role exists?
        if not cls.role_exists(role_name):
            new_role = cls(role_name=role_name)
            db.session.add(new_role)
            db.session.commit()
            print("added new role")

    @classmethod
    def initialize(cls):
        ProjectRole.create_role("Read")
        ProjectRole.create_role("Suggest")
        ProjectRole.create_role("Vote")
        ProjectRole.create_role("Accept")
        ProjectRole.create_role("Edit")
        ProjectRole.create_role("Owner")
