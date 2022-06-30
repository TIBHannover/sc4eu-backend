from extensions import db

from .user_model import UserModel
from .project_model import ProjectModel


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

        print("Here my lord")
        print(user_project_to_delete_exists)
        if user_project_to_delete_exists:
            to_delete_entries = db.session.query(UsersProjects).filter_by(user_id=user_id).all()

            for delete_entry in to_delete_entries:
                db.session.delete(delete_entry)
                db.session.commit()
            return True
        return False

    @classmethod
    def delete_user_projects(cls, user_id, projects_id):
        res = False
        # for project_id in projects_id:
        #     res = cls.delete_user_project(user_id, project_id.id)
        res = cls.delete_user_project(user_id)
        return res

    @classmethod
    def add_user_project(cls, user_id, project_id):

        # user_id = UserModel.get_user_id_for_uuid(user_uuid).id
        # project_id = ProjectModel.get_project_id_for_uuid(user_uuid).id

        user_project_to_add_does_not_exists = db.session.query(UsersProjects).filter_by(user_id=user_id,
                                                                                        project_id=project_id).first() is None
        if user_project_to_add_does_not_exists:
            new_entry = UsersProjects()
            new_entry.user_id = user_id
            new_entry.project_id = project_id

            db.session.add(new_entry)
            db.session.commit()
            return True
        return False

    @classmethod
    def add_user_projects(cls, user_id, projects_uuid):
        res = False
        for project_uuid in projects_uuid:
            project_id = ProjectModel.get_project_id_for_uuid(project_uuid)
            res = cls.add_user_project(user_id, project_id)
        return res

    # This method first delete all existing user projects and then
    # it adds the new list. Maybe Not the Most efficient way, so make it more efficient
    @classmethod
    def update_user_projects(cls, user_uuid, projects_id):
        userId = UserModel.get_user_id_for_uuid(user_uuid)
        # Get all projects for this user_id
        user_all_projects = db.session.query(UsersProjects).filter_by(user_id=userId).all()
        print(user_all_projects)
        if user_all_projects:
            res = cls.delete_user_projects(userId, user_all_projects)
        res = cls.add_user_projects(userId, projects_id)

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
