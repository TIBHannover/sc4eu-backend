from extensions import db
from uuid import uuid4
from ._base import ModelMixin


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'sc3_role_model'
    id = db.Column('id', db.Integer(), primary_key=True)
    name = db.Column('name', db.String(50), unique=True)

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
        Role.create_role("User")
        Role.create_role("Member")
        Role.create_role("Admin")


class UsersRoles(db.Model):
    __tablename__ = 'sc3_users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('sc3UserModel.hash_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('sc3_role_model.id', ondelete='CASCADE'))
