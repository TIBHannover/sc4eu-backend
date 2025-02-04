from extensions import db
from uuid import uuid4
from flask import jsonify
from passlib.hash import sha256_crypt
from libgravatar import Gravatar
from ._base import ModelMixin
from .role_model import Role
from .user_roles import UsersRoles
from sqlalchemy.dialects.postgresql.base import UUID
import os

# do we import session here? <<<<

# CONSTANTS DEF
AUTH_GITHUB = "AUTH_GITHUB"
AUTH_LOCAL = "AUTH_LOCAL"
AUTH_TOKEN = "AUTH_TOKEN"
AUTH_GITLAB = "AUTH_GITLAB"
AUTH_GOOGLE = "AUTH_GOOGLE"
AUTH_SAP = "AUTH_SAP"


class UserModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_user_model'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid = db.Column('uuid', UUID(as_uuid=True), unique=True, default=uuid4)
    display_name = db.Column('display_name', db.String)
    email_address = db.Column('email_address', db.String)
    passwd_hash = db.Column('passwd_hash', db.String)
    auth_type = db.Column('auth_type', db.String)
    email_valid = db.Column('email_valid', db.Boolean, default=False)
    active = db.Column('account_active', db.Boolean, default=True)  # admin could disable accounts

    # Relationships
    roles = db.relationship('Role', secondary='sc3_users_roles',
                            backref=db.backref('sc3_user_model', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)

    @classmethod
    def initialize_admin_user(cls):
        if os.environ["ADMIN_ADDRESS"]:
            user = UserModel.query.filter_by(email_address=os.environ["ADMIN_ADDRESS"]).first()
            if user is None:
                print("there is no admin user, creating one! ")
                new_entry = UserModel()
                new_entry.auth_type = AUTH_LOCAL
                new_entry.display_name = "System ADMIN"
                # // assign default role
                _user_role = Role.query.filter(Role.name == 'System Admin').first()
                new_entry.roles = [_user_role]  # default user role
                new_entry.email_address = os.environ["ADMIN_ADDRESS"]
                new_entry.passwd_hash = sha256_crypt.encrypt(os.environ["ADMIN_SECRET"])
                new_entry.email_valid = True

                db.session.add(new_entry)
                db.session.commit()

            # create a User

    @classmethod
    def get_header_info_for_user(cls, user_id, token):
        # check if token is valid
        token_valid = sha256_crypt.verify(user_id, token)
        if token_valid:
            user = UserModel.query.filter_by(uuid=user_id).first()
            if user:
                is_email_valid = cls.is_email_valid(user.email_address)
                if is_email_valid:
                    name = user.display_name
                    email = user.email_address
                    g = Gravatar(email)
                    gravatar_id = g.email_hash
                    role = cls.get_user_role_for_id(user_id)
                    print({"displayName": name, "gravatarId": gravatar_id, "userId": user.uuid, "role": role,
                           "is_email_valid": is_email_valid})
                    return {"displayName": name, "userEmail": email, "gravatarId": gravatar_id, "userId": user.uuid,
                            "role": role}
                else:
                    return {"error": "User is not verified"}
            else:
                return {"error": "Invalid Token or User"}
        else:
            return {"error": "Invalid Token"}

    @classmethod
    def find_or_login_user(cls, params):
        if params['auth_type'] == AUTH_LOCAL:
            exists = cls.exists_in_db(params['email'])
            is_email_valid = cls.is_email_valid(params['email'])

            if exists:
                user = db.session.query(UserModel).filter_by(email_address=params['email']).first()
                if is_email_valid:
                    res = cls.getUser(params)
                    # create a bToken
                    # we create an ssh encryption using the user id
                    if (res["success"]):
                        res['bToken'] = sha256_crypt.encrypt(res['user_id'])
                    return res
                else:
                    return {
                        "is_email_valid": False,
                        "user_id": str(user.uuid),
                        "displayName": str(user.display_name),
                        "success": False,
                        "error": "Your email is not verified. Please Click on the link that has just been sent your "
                                 "email account to verify your email than Sign In"}
            else:
                return {
                    "success": False,
                    "error": "Error: No such user exists"}

        if params['auth_type'] == AUTH_GITHUB:
            res = {'user_id': params['user_id']}
            res['bToken'] = sha256_crypt.encrypt(res['user_id'])
            return res

        if params['auth_type'] == AUTH_GITLAB:
            res = {'user_id': params['user_id']}
            res['bToken'] = sha256_crypt.encrypt(res['user_id'])
            return res
        
        if params['auth_type'] == AUTH_GOOGLE:
            res = {'user_id': params['user_id']}
            res['bToken'] = sha256_crypt.encrypt(res['user_id'])
            return res
        
        if params['auth_type'] == AUTH_SAP:
            res = {'user_id': params['user_id']}
            res['bToken'] = sha256_crypt.encrypt(res['user_id'])
            return res
        
        else:  # TOKEN BASED THINGY???
            return cls.getUserFromToken(params)

    @classmethod
    def get_user_from_token(cls, params):
        return {"error": "Error: Not implemented Yet~! "}

    @classmethod
    def find_or_create_user(cls, params):
        # params is an object holding information

        if params['auth_type'] == AUTH_GITHUB:
            exists = cls.exists_in_db(params['email'])
            if not exists:
                cls.create_user(params)

            return cls.getUser(params)

        if params['auth_type'] == AUTH_GITLAB:
            exists = cls.exists_in_db(params['email'])
            if not exists:
                cls.create_user(params)
            return cls.getUser(params)
        
        if params['auth_type'] == AUTH_GOOGLE:
            exists = cls.exists_in_db(params['email'])
            if not exists:
                cls.create_user(params)
            return cls.getUser(params)
        
        if params['auth_type'] == AUTH_SAP:
            exists = cls.exists_in_db(params['email'])
            if not exists:
                cls.create_user(params)
            return cls.getUser(params)

        if params['auth_type'] == AUTH_LOCAL:
            exists = cls.exists_in_db(params['email'])
            if not exists:
                cls.create_user(params)

            # we need to see if that thing is correctly to login ?
            return cls.getUser(params)

    @classmethod
    def getUser(cls, params):
        email = params.get('email')
        auth_type = params.get('auth_type')
        if auth_type == AUTH_LOCAL:
            passwd = params.get('passwd')
            pass_hash = db.session.query(UserModel.passwd_hash).filter_by(email_address=email).first()
            if pass_hash[0] is None:  # Access the first element of the tuple
                return {"success": False, "error": "Incorrect Password"}
            correct_credentials = sha256_crypt.verify(passwd, pass_hash[0])
            if correct_credentials:
                # returning an object for the express server to create the jwt token
                user = db.session.query(UserModel).filter_by(email_address=email).first()
                return {"success": True, "user_id": str(user.uuid)}
            else:
                return {"success": False, "error": "Incorrect Password"}

        if auth_type == AUTH_GITHUB:
            # we receive the jwt token?
            user = db.session.query(UserModel).filter_by(email_address=email).first()
            return {"user_id": str(user.uuid)}

        if auth_type == AUTH_GITLAB:
            user = db.session.query(UserModel).filter_by(email_address=email).first()
            return {"user_id": str(user.uuid)}
        
        if auth_type == AUTH_GOOGLE:
            user = db.session.query(UserModel).filter_by(email_address=email).first()
            return {"user_id": str(user.uuid)}
        
        if auth_type == AUTH_SAP:
            user = db.session.query(UserModel).filter_by(email_address=email).first()
            return {"user_id": str(user.uuid)}

        else:
            return False

    @classmethod
    def delete_user(cls, user_uuid):

        user_to_delete_exists = db.session.query(UserModel.uuid).filter_by(uuid=user_uuid).first() is not None

        if user_to_delete_exists:
            to_delete_entry = db.session.query(UserModel).filter_by(uuid=user_uuid).first()
            user_id = to_delete_entry.id
            print(to_delete_entry, flush=True)
            db.session.delete(to_delete_entry)
            db.session.commit()
            UsersRoles.delete_user_role(user_id)
            return {"success": "true"}
        return {"success": "false"}

    @classmethod
    def update_user_role(cls, user_uuid, user_role):

        user_to_update_exists = db.session.query(UserModel.uuid).filter_by(uuid=user_uuid).first() is not None

        if user_to_update_exists:
            to_delete_entry = db.session.query(UserModel).filter_by(uuid=user_uuid).first()
            user_id = to_delete_entry.id
            UsersRoles.update_user_role(user_id, user_role)
            return "true"
        return "false"

    @classmethod
    def get_all_users_for_dashboard(cls):
        return UserModel.query.order_by(UserModel.created_at.desc()).all()

    @classmethod
    def get_user_role_for_id(cls, user_id):
        user_roles = db.session.query(UserModel).filter_by(uuid=user_id).first()
        return user_roles.roles[0].name

    @classmethod
    def exists_in_db(cls, email):
        if not email or len(email) == 0:
            return False
        else:
            return db.session.query(UserModel.email_address).filter_by(email_address=email).first() is not None

    @classmethod
    def is_email_valid(cls, email):
        is_email_exists = db.session.query(UserModel).filter_by(
            email_address=email).first() is not None

        if is_email_exists:
            user_email_valid = db.session.query(UserModel).filter_by(email_address=email).first()
            if not user_email_valid.email_valid:
                return False
            else:
                return db.session.query(UserModel.email_address).filter_by(email_address=email).first() is not None

    # This method should only be allowed to be used for users with role ADMIN!
    @classmethod
    def getAllUsers(cls):
        result = UserModel.query.order_by(UserModel.created_at.desc()).all()
        if len(result) == 0:
            return False
        else:
            return result

    @classmethod
    def get_user_id_for_uuid(cls, uuid_user):
        user_id = db.session.query(UserModel).filter_by(uuid=uuid_user).first()
        return user_id.id

    @classmethod
    def create_user(cls, params):
        # generic user function
        # we receive params from server and then decide what to do
        auth_type = params['auth_type']
        if auth_type == AUTH_LOCAL:
            res = cls.create_user_from_email(params)
            return res
        if auth_type == AUTH_GITHUB:
            return cls.create_user_github(params)
        if auth_type == AUTH_GITLAB:
            return cls.create_user_gitlab(params)
        if auth_type == AUTH_GOOGLE:
            return cls.create_user_google(params)
        if auth_type == AUTH_SAP:
            return cls.create_user_sap(params)

    @classmethod
    def create_user_github(cls, params):
        new_entry = UserModel()
        new_entry.auth_type = params['auth_type']
        new_entry.display_name = params['display_name']
        new_entry.email_address = params['email']
        new_entry.email_valid = params['email_valid']
        # // assign default role
        _user_role = Role.query.filter(Role.name == 'Public User').first()
        new_entry.roles = [_user_role]  # default user role
        # add to db
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def create_user_gitlab(cls, params):
        new_entry = UserModel()
        new_entry.auth_type = params['auth_type']
        new_entry.display_name = params['display_name']
        new_entry.email_address = params['email']
        new_entry.email_valid = params['email_valid']
        # // assign default role
        _user_role = Role.query.filter(Role.name == 'Public User').first()
        new_entry.roles = [_user_role]  # default user role
        # add to db
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def create_user_google(cls, params):
        new_entry = UserModel()
        new_entry.auth_type = params['auth_type']
        new_entry.display_name = params['display_name']
        new_entry.email_address = params['email']
        new_entry.email_valid = params['email_valid']
        # // assign default role
        _user_role = Role.query.filter(Role.name == 'Public User').first()
        new_entry.roles = [_user_role]  # default user role
        # add to db
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def create_user_sap(cls, params):
        new_entry = UserModel()
        new_entry.auth_type = params['auth_type']
        new_entry.display_name = params['display_name']
        new_entry.email_address = params['email']
        new_entry.email_valid = params['email_valid']
        # // assign default role
        _user_role = Role.query.filter(Role.name == 'Public User').first()
        new_entry.roles = [_user_role]  # default user role
        # add to db
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def create_user_from_email(cls, params):
        # validate email params:
        valid = False
        if 'username' in params.keys():
            if 'password' in params.keys():
                valid = True

        if valid:
            # check if user already exists
            if cls.exists_in_db(params['username']):
                return {"task": "create user from email", "success": False, "error": "Email already registered"}

            new_entry = UserModel()
            new_entry.auth_type = params['auth_type']
            new_entry.display_name = params['displayName']
            # // assign default role
            _user_role = Role.query.filter(Role.name == 'Public User').first()
            new_entry.roles = [_user_role]  # default user role

            new_entry.email_address = params['username']
            passwd = params['password']
            if len(passwd) == 0:
                return {"task": "create user from email", "success": False, "error": "Something Went wrong"}

            new_entry.passwd_hash = sha256_crypt.encrypt(passwd)

            # add to db
            db.session.add(new_entry)
            db.session.commit()
            return {"task": "create user from email", "success": True, "user_id": str(new_entry.uuid),
                    "bToken": sha256_crypt.encrypt(str(new_entry.uuid))}
        else:
            return {"task": "create user from email", "success": False, "error": "Invalid Parameters"}

    @classmethod
    def update_user_settings(cls, user_id, token, params):
        if token:
            try:
                token_valid = sha256_crypt.verify(user_id, token)
                if token_valid:
                    user = UserModel.query.filter_by(uuid=user_id).first()
                    # todo validate if thing exists at all? but should be
                    # todo some mappings of the params to the individual entry
                    user.display_name = params['username']
                    db.session.commit()

                    return {"success": True}

            except:
                return {"error": "You dont have permission on this page"}

    @classmethod
    def get_profile_info(cls, user_id, token):
        user = UserModel.query.filter_by(uuid=user_id).first()
        g = Gravatar(user.email_address)
        gravatar_id = g.email_hash
        if token:
            try:
                token_valid = sha256_crypt.verify(user_id, token)

                if token_valid:

                    # todo : what does a user need in his profile????
                    res = {"user": {"name": user.display_name,
                                    "email": user.email_address,
                                    "auth_type": user.auth_type,
                                    "valid_email": user.email_valid,
                                    "gravatarId": gravatar_id,
                                    }
                           }
                    return res
                    # todo: request project information
                else:
                    return {"error": "You dont have permission on this page"}
            except:
                return {"error": "You dont have permission on this page"}

        else:
            # just the view of a profile

            res = {"user": {"name": user.display_name,
                            "gravatarId": gravatar_id
                            }
                   }
            # todo: request project information
            return res

    @classmethod
    def edit_email_valid(cls, uuid):
        user_to_update_exists = db.session.query(UserModel).filter_by(
            uuid=uuid).first() is not None

        if user_to_update_exists:
            user_email_valid = db.session.query(UserModel).filter_by(uuid=uuid).first()
            user_email_valid.email_valid = True

            db.session.commit()

    @classmethod
    def update_password(cls, uuid, password):
        user_to_update_exists = db.session.query(UserModel).filter_by(
            uuid=uuid).first() is not None

        if user_to_update_exists:
            user_password = db.session.query(UserModel).filter_by(uuid=uuid).first()
            user_password.passwd_hash = sha256_crypt.encrypt(password)

            db.session.commit()
            return {"success": True, "message": "Password changed successfully "}

        return {"success": False, "message": "something went wrong please try again after some time"}

    @classmethod
    def is_email_exists(cls, email):
        email_exists = db.session.query(UserModel).filter_by(
            email_address=email).first() is not None
        if email_exists:
            user = db.session.query(UserModel).filter_by(email_address=email).first()
            return {"success": True, "message": "Email is exist", "user_id": str(user.uuid),
                    "display_name": str(user.display_name)}

        return {"success": False, "message": "Email does not exist"}

    @classmethod
    def get_user_detail_by_id(cls, user_id):
        user = UserModel.query.filter_by(id=user_id).first()
        if user:
            userDetailObject = {"uuid": user.uuid, "display_name": user.display_name,
                                "email_address": user.email_address, "auth_type": user.auth_type,
                                "email_valid": user.email_valid, "active": user.active, "role": user.roles[0].name}
            return userDetailObject
        return None

    # Todo: refactor get_All_System_Admin methode instead of for loop try to use query
    @classmethod
    def get_All_System_Admin(cls):
        users = UserModel.query.order_by(UserModel.created_at.desc()).all()
        if users:
            allSystem_Admin = []
            for user in users:
                if user.roles[0].name == "System Admin":
                    system_admin = {"uuid": user.uuid,
                                    "auth_type": user.auth_type,
                                    "display_name": user.display_name,
                                    "email_valid": user.email_valid,
                                    "email_address": user.email_address,
                                    "role": user.roles[0].name
                                    }
                    allSystem_Admin.append(system_admin)
            return jsonify(allSystem_Admin)
        else:
            return jsonify({'error': "No system admin found"})
