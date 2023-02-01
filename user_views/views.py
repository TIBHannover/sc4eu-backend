from flask import jsonify, request, json
from flask.views import MethodView
from util import use_args_with
from ._params import UserHeaderGetParams, ViewProfileArgs, UserProjectsGetParams, UserRoleArgs
from models import UserModel, Role, UsersRoles, UsersProjects
from functools import wraps


def requires_role(allowed_roles, *outer_args, **outer_kwargs):
    def wrapper(view_function, *wrapper_args, **wrapper_kwargs):
        for x in wrapper_args:
            print("OuterAgs:" + x)

        for x in wrapper_kwargs.values():
            print("Outer KAgs:" + x)

        @wraps(view_function)  # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):
            # user_manager = current_app.user_manager

            # check if user has role ???
            user_role = UserModel.get_user_role_for_id(outer_args[0])
            if user_role in allowed_roles:
                # It's OK to call the view
                return view_function(*args, **kwargs)
            else:
                # not okay to call the view_function
                return {"error": "Role not match"}

        return decorator

    return wrapper


class UserAPIRegister(MethodView):
    def post(self):
        result = UserModel.create_user(request.json)
        return jsonify(result)


class UserAPILogin(MethodView):

    def post(self):
        auth_type = request.json['auth_type']
        res = ''
        # local : email passwd login
        if auth_type == "AUTH_LOCAL":
            res = UserModel.find_or_login_user(
                {'email': request.json['username'], 'auth_type': request.json['auth_type'],
                 'passwd': request.json['password']})

        # ----------- CURRENTLY NOT USER AT ALL --------------
        # token based login
        if auth_type == "AUTH_TOKEN":
            # we assume this is a token based authorization
            res = UserModel.find_or_login_user({'token': request.json['token']})

        # GitHub auth
        if auth_type == "AUTH_GITHUB":
            # we assume this is a token based authorization
            user = UserModel.find_or_create_user(
                {'email': request.json['email'], 'display_name': request.json['displayName'],
                 'auth_type': request.json['auth_type'], 'email_valid': True})
            res = UserModel.find_or_login_user({'user_id': user['user_id'],
                                                'auth_type': request.json['auth_type']})

        # Gitlab auth
        if auth_type == "AUTH_GITLAB":
            # we assume this is a token based authorization
            user = UserModel.find_or_create_user(
                {'email': request.json['email'], 'display_name': request.json['displayName'],
                 'auth_type': request.json['auth_type'], 'email_valid': True})
            res = UserModel.find_or_login_user({'user_id': user['user_id'],
                                                'auth_type': request.json['auth_type']})

        return jsonify(res)


class UserDelete(MethodView):
    @use_args_with(UserHeaderGetParams)
    def get(self, reqargs):
        if reqargs.get("userId"):
            user_id = reqargs.get("userId")
            res = UserModel.delete_user(user_id)
            return res
        return jsonify({'error': "No user found"})


class UserHeader(MethodView):
    @use_args_with(UserHeaderGetParams)
    def get(self, reqargs):
        if reqargs.get("userId"):
            user_id = reqargs.get("userId")
            token = reqargs.get("token")
            res = UserModel.get_header_info_for_user(user_id, token)
            return jsonify(res)

        return jsonify({'error': "No user found"})


class AdminDashboard(MethodView):
    @use_args_with(UserHeaderGetParams)
    def get(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        allowed_roles = ["Admin", "System Admin", "Project Admin"]

        @requires_role(allowed_roles, user_id, token)
        def execute():
            users = UserModel.get_all_users_for_dashboard()
            if users:
                all_users = [{"uuid": user.uuid,
                              "auth_type": user.auth_type,
                              "display_name": user.display_name,
                              "email_valid": user.email_valid,
                              "email_address": user.email_address,
                              "role": user.roles[0].name
                              }
                             for user in users]
                return jsonify(all_users)
            else:
                return jsonify({'error': "Something went wrong"})

        return execute()

        #

        # default return


class ViewProfile(MethodView):
    @use_args_with(ViewProfileArgs)
    def get(self, reqargs):
        if reqargs.get("userId"):
            user_id = reqargs.get("userId")
            token = reqargs.get("token")

            if token:
                res = UserModel.get_profile_info(user_id, token)
            else:
                res = UserModel.get_profile_info(user_id, token)
            return jsonify(res)

        return jsonify({'error': "No user found"})

    @use_args_with(ViewProfileArgs)
    def post(self, reqargs):
        print("THIS IS THE PUT REQUEST")
        print(reqargs)
        print(request.json)
        print(">>>>>")

        if request.json:
            user_id = reqargs.get("userId")
            token = reqargs.get("token")

            return jsonify(UserModel.update_user_settings(user_id, token, request.json))
        else:
            return jsonify({"error": "no information updated"})


class UpdateUserRole(MethodView):
    @use_args_with(UserRoleArgs)
    def post(self, reqargs):

        if request.json:
            user_id = request.json["userId"]
            user_role = request.json["userRole"]
            return jsonify(UserModel.update_user_role(user_id, user_role))
        else:
            return jsonify({"error": "no information updated"})


class GetUserRole(MethodView):
    @use_args_with(UserRoleArgs)
    def get(self, reqargs):
        userUUID = reqargs["userId"]
        if userUUID:
            return jsonify(UserModel.get_user_role_for_id(userUUID))
        else:
            return jsonify({"error": "No role found for the user"})


class GetAllRoles(MethodView):
    @use_args_with(UserHeaderGetParams)
    def get(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")
        allowed_roles = ["Admin", "System Admin", "Project Admin"]

        @requires_role(allowed_roles, user_id, token)
        def execute():
            roles = Role.get_all_roles()
            if roles:
                all_roles = [{
                    "role": role.name,
                    "role_id": role.id
                }
                    for role in roles]
                return jsonify(all_roles)
            else:
                return jsonify({'error': "Something went wrong"})

        return execute()


class UpdateUserProjects(MethodView):
    @use_args_with(UserProjectsGetParams)
    def post(self, reqargs):

        if request.json:
            userId = request.json["userId"]
            projectsId = request.json["projectsId"]
            if userId:
                return UsersProjects.update_user_projects(userId, projectsId)
        else:
            return {
                "success": False,
                "error": "No user Project Combination Updated"
            }


class GetUserProjects(MethodView):
    @use_args_with(UserProjectsGetParams)
    def get(self, reqargs):
        userUUID = reqargs["userId"]
        user_id = UserModel.get_user_id_for_uuid(userUUID)

        if user_id:
            res = jsonify(UsersProjects.get_user_projects(user_id))
            return res
        return jsonify({'error': "No projects found for the user"})


class EditEmailValid(MethodView):
    def post(self):
        if request.json:
            uuid = request.json["uuid"]

            UserModel.edit_email_valid(uuid)
            return jsonify({"result": True, "Edit": 'successful'})

        else:
            return jsonify({"result": False, "error": "no information updated"})


class EmailExists(MethodView):
    def post(self):
        if request.json:
            email = request.json["email_address"]
            res = UserModel.is_email_exists(email)
            return res

        return jsonify({"successful": False, "message": "something went wrong please try again after some time"})


class SetNewPassword(MethodView):
    def post(self):
        if request.json:
            user_id = request.json["user_id"]
            password = request.json["password"]

            res = UserModel.update_password(user_id, password)
            return res

        return jsonify({"success": False, "message": "something went wrong please try again after some time"})

class GetAllUsers(MethodView):
    def get(self):
        def execute():
            users = UserModel.get_all_users_for_dashboard()
            if users:
                all_users = [{"uuid": user.uuid,
                              "auth_type": user.auth_type,
                              "display_name": user.display_name,
                              "email_valid": user.email_valid,
                              "email_address": user.email_address,
                              "role": user.roles[0].name
                              }
                             for user in users]
                return jsonify(all_users)
            else:
                return jsonify({'error': "Something went wrong"})

        return execute()