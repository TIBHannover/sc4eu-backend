from extensions import db

class UsersRoles(db.Model):
    __tablename__ = 'sc3_users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('sc3_user_model.hash_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('sc3_role_model.id', ondelete='CASCADE'))
