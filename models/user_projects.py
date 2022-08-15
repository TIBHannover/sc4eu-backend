from extensions import db
from sqlalchemy.exc import SQLAlchemyError

from .project_model import ProjectModel
from .user_model import UserModel


class UsersProjects(db.Model):
    __tablename__ = 'sc3_users_projects'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('sc3_user_model.hash_id', ondelete='CASCADE'))
    project_id = db.Column(db.Integer(), db.ForeignKey('projects_table.hash_id', ondelete='CASCADE'))

    @classmethod
    def delete_user_project(cls, user_id):
        # Get ids for user_uuid and project_uuid
        # user_id = UserModel.get_user_id_for_uuid(user_uuid).id
        # project_id = ProjectModel.get_project_id_for_uuid(project_uuid).id
        user_project_to_delete_exists = db.session.query(UsersProjects).filter_by(user_id=user_id, ).first() is not None

        if user_project_to_delete_exists:
            try:
                db.session.query(UsersProjects).filter_by(user_id=user_id).delete()
                db.session.commit()
            except:
                db.session.rollback()
        return True

    @classmethod
    def delete_user_projects(cls, user_id):
        res = {"success": True}
        result = cls.delete_user_project(user_id)
        if not result:
            return False
        return res

    @classmethod
    def add_user_project(cls, user_id, project_id):

        # user_id = UserModel.get_user_id_for_uuid(user_uuid).id
        # project_id = ProjectModel.get_project_id_for_uuid(user_uuid).id

        new_entry = UsersProjects()
        new_entry.user_id = user_id
        new_entry.project_id = project_id
        try:
            db.session.add(new_entry)
            db.session.commit()
        except SQLAlchemyError as e:
            return False
        return True

    @classmethod
    def add_user_projects(cls, user_id, projects_uuid):
        res = {"success": True}
        for project_uuid in projects_uuid:
            project_id = ProjectModel.get_project_id_for_uuid(project_uuid)
            user_project_to_add_does_not_exists = db.session.query(UsersProjects).filter_by(user_id=user_id,
                                                                                            project_id=project_id).first() is None
            if user_project_to_add_does_not_exists:
                result = cls.add_user_project(user_id, project_id)
                if not result:
                    return False
        return res

    # This method first delete all existing user projects and then
    # it adds the new list. Maybe Not the Most efficient way, so make it more efficient
    @classmethod
    def update_user_projects(cls, user_uuid, projects_id):
        res = {"success": True}
        userId = UserModel.get_user_id_for_uuid(user_uuid)
        # Get all projects for this user_id
        user_all_projects = db.session.query(UsersProjects).filter_by(user_id=userId).all()

        # if user_all_projects is empty, Nothing to delete
        if user_all_projects:
            res = cls.delete_user_projects(userId)
            if not res:
                return {
                    "success": False,
                    "error": "Something went wrong while updating user projects"
                }

        # if project_id is null nothing to add
        if projects_id:
            res = cls.add_user_projects(userId, projects_id)
            if not res:
                return {
                    "success": False,
                    "error": "Something went wrong while updating user projects"
                }
        return res

    # This method update all projects for all modified users
    # This method may not be used for now. Maybe in future if we want to do batch update
    @classmethod
    def update_users_projects(cls, users_id, projects_id):
        res = False
        for user_id in users_id:
            # Get all projects for this user_id
            res = cls.update_user_projects(user_id, projects_id)
        return res

    @classmethod
    def get_user_projects(cls, user_id):
        projects = []
        user_all_projects = db.session.query(UsersProjects).filter_by(user_id=user_id).all()
        if user_all_projects:
            for user_project in user_all_projects:
                print(user_project.project_id)
                project_uuid = ProjectModel.get_project_by_id(user_project.project_id).uuid
                projects.append(project_uuid)
        return projects
