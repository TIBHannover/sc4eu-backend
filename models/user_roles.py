from extensions import db

class UsersRoles(db.Model):
    __tablename__ = 'sc3_users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('sc3_user_model.hash_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('sc3_role_model.id', ondelete='CASCADE'))

    @classmethod
    def delete_user_role(cls, user_id):
        user_role_to_delete_exists = db.session.query(UsersRoles).filter_by(user_id=user_id).first() is not None

        if user_role_to_delete_exists:
            to_delete_entry = db.session.query(UsersRoles).filter_by(user_id=user_id).first()
            db.session.delete(to_delete_entry)
            db.session.commit()

    @classmethod
    def get_user_role(self, user_id):
        user_role_exists = db.session.query(UsersRoles).filter_by(user_id=user_id).first() is not None
        if user_role_exists:
            the_entry = db.session.query(UsersRoles).filter_by(user_id=user_id).first()
            return the_entry.role_id

    @classmethod
    def update_user_role(cls, user_id, user_role):
        user_role_to_update_exists = db.session.query(UsersRoles).filter_by(user_id=user_id).first() is not None
        if user_role_to_update_exists:
            to_update_entry = db.session.query(UsersRoles).filter_by(user_id=user_id).first()
            to_update_entry.role_id = user_role
            db.session.commit()
