from flask import jsonify, request, Blueprint
from util import use_args_with
from ._params import (
    UserHeaderGetParams,
    ViewProfileArgs,
    UserProjectsGetParams,
    UserRoleArgs,
    UserEmailArgs,
)
from models import UserModel, Role, UsersProjects, ProjectModel
from functools import wraps

users_blueprint = Blueprint("users", __name__)


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

#TODO: Find out if e-mail isn't send after API change
@users_blueprint.route("/users/register/", methods=["POST"])
def register_user():
    result = UserModel.create_user(request.json)
    return jsonify(result)


@users_blueprint.route("/users/login/", methods=["POST"])
def user_login():

    auth_type = request.json.get("auth_type")
    res = ""
    # local : email passwd login
    if auth_type == "AUTH_LOCAL":
        res = UserModel.find_or_login_user(
            {
                "email": request.json["username"],
                "auth_type": request.json["auth_type"],
                "passwd": request.json["password"],
            }
        )

    # ----------- CURRENTLY NOT USER AT ALL --------------
    # token based login
    if auth_type == "AUTH_TOKEN":
        # we assume this is a token based authorization
        res = UserModel.find_or_login_user({"token": request.json["token"]})

    # GitHub auth
    if auth_type == "AUTH_GITHUB":
        # we assume this is a token based authorization
        user = UserModel.find_or_create_user(
            {
                "email": request.json["email"],
                "display_name": request.json["displayName"],
                "auth_type": request.json["auth_type"],
                "email_valid": True,
            }
        )
        res = UserModel.find_or_login_user(
            {"user_id": user["user_id"], "auth_type": request.json["auth_type"]}
        )

    # Gitlab auth
    if auth_type == "AUTH_GITLAB":
        # we assume this is a token based authorization
        user = UserModel.find_or_create_user(
            {
                "email": request.json["email"],
                "display_name": request.json["displayName"],
                "auth_type": request.json["auth_type"],
                "email_valid": True,
            }
        )
        res = UserModel.find_or_login_user(
            {"user_id": user["user_id"], "auth_type": request.json["auth_type"]}
        )

    # Google auth
    if auth_type == "AUTH_GOOGLE":
        # we assume this is a token based authorization
        user = UserModel.find_or_create_user(
            {
                "email": request.json["email"],
                "display_name": request.json["displayName"],
                "auth_type": request.json["auth_type"],
                "email_valid": True,
            }
        )
        res = UserModel.find_or_login_user(
            {"user_id": user["user_id"], "auth_type": request.json["auth_type"]}
        )

    # SAP auth
    if auth_type == "AUTH_SAP":
        # we assume this is a token based authorization
        user = UserModel.find_or_create_user(
            {
                "email": request.json["email"],
                "display_name": request.json["displayName"],
                "auth_type": request.json["auth_type"],
                "email_valid": True,
            }
        )
        res = UserModel.find_or_login_user(
            {"user_id": user["user_id"], "auth_type": request.json["auth_type"]}
        )

    return jsonify(res)


@users_blueprint.route("/users/delete/", methods=["GET"])
@use_args_with(UserHeaderGetParams)
def users_delete(reqargs):
    if reqargs.get("userId"):
        user_id = reqargs.get("userId")
        res = UserModel.delete_user(user_id)
        return res
    return jsonify({"error": "No user found"})


@users_blueprint.route("/users/header/", methods=["get"])
@use_args_with(UserHeaderGetParams)
def users_header(reqargs):
    if reqargs.get("userId"):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")
        res = UserModel.get_header_info_for_user(user_id, token)
        return jsonify(res)

    return jsonify({"error": "No user found"})


@users_blueprint.route("/admin/dashboard/", methods=["GET", "POST"])
@use_args_with(UserHeaderGetParams)
def admin_dashboard(reqargs):
    user_id = reqargs.get("userId")
    token = reqargs.get("token")
    print("is user id exist ?")
    allowed_roles = ["Admin", "System Admin", "Project Admin"]

    @requires_role(allowed_roles, user_id, token)
    def execute():
        users = UserModel.get_all_users_for_dashboard()
        if users:
            all_users = [
                {
                    "uuid": str(user.uuid),
                    "auth_type": user.auth_type,
                    "display_name": user.display_name,
                    "email_valid": user.email_valid,
                    "email_address": user.email_address,
                    "role": user.roles[0].name,
                }
                for user in users
            ]
            return jsonify(all_users)
        else:
            return jsonify({"error": "Something went wrong"})

    return execute()


@users_blueprint.route("/users/viewProfile/", methods=["GET"])
@use_args_with(ViewProfileArgs)
def view_profile(reqargs):
    if reqargs.get("userId"):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        res = UserModel.get_profile_info(user_id, token)

        return jsonify(res)

    return jsonify({"error": "No user found"})


@users_blueprint.route("/users/viewProfile/", methods=["POST"])
@use_args_with(ViewProfileArgs)
def view_profile_post(reqargs):
    if request.json:
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        return jsonify(UserModel.update_user_settings(user_id, token, request.json))
    else:
        return jsonify({"error": "no information updated"})


@users_blueprint.route("/users/updateUserRole/", methods=["POST"])
@use_args_with(UserRoleArgs)
def update_user_role(reqargs):

    if request.json:
        user_id = request.json["userId"]
        user_role = request.json["userRole"]
        return jsonify(UserModel.update_user_role(user_id, user_role))
    else:
        return jsonify({"error": "no information updated"})


@users_blueprint.route("/user/role/", methods=["GET"])
@use_args_with(UserRoleArgs)
def get_user_role(reqargs):
    userUUID = reqargs["userId"]
    if userUUID:
        return jsonify(UserModel.get_user_role_for_id(userUUID))
    else:
        return jsonify({"error": "No role found for the user"})


@users_blueprint.route("/roles/all/", methods=["GET"])
@use_args_with(UserHeaderGetParams)
def get_roles(reqargs):
    user_id = reqargs.get("userId")
    token = reqargs.get("token")
    allowed_roles = ["Admin", "System Admin", "Project Admin"]

    @requires_role(allowed_roles, user_id, token)
    def execute():
        roles = Role.get_all_roles()
        if roles:
            all_roles = [{"role": role.name, "role_id": role.id} for role in roles]
            return jsonify(all_roles)
        else:
            return jsonify({"error": "Something went wrong"})

    return execute()


@users_blueprint.route("/users/updateUserProjects/", methods=["POST"])
@use_args_with(UserProjectsGetParams)
def update_user_projects(reqargs):
    if request.json:
        userId = request.json["userId"]
        projectsId = request.json["projectsId"]
        if userId:
            return UsersProjects.update_user_projects(userId, projectsId)
        else:
            return jsonify(
                {"success": False, "error": "No user Project Combination Updated"}
            ), 400
    else:
        return jsonify(
            {"success": False, "error": "No user Project Combination Updated"}
        )


@users_blueprint.route("/user/projects/", methods=["GET"])
@use_args_with(UserProjectsGetParams)
def gget_user_projectset(reqargs):
    userUUID = reqargs["userId"]
    user_id = UserModel.get_user_id_for_uuid(userUUID)

    if user_id:
        res = jsonify(UsersProjects.get_user_projects(user_id))
        return res
    return jsonify({"error": "No projects found for the user"})


@users_blueprint.route("/user/projectsDetail/", methods=["GET"])
@use_args_with(UserProjectsGetParams)
def get_user_projects_detail(reqargs):
    userUUID = reqargs["userId"]
    user_id = UserModel.get_user_id_for_uuid(userUUID)

    if user_id:
        res = jsonify(UsersProjects.get_user_projects_detail(user_id))
        return res
    return jsonify({"error": "No projects found for the user"})


@users_blueprint.route("/project/usersDetail/", methods=["GET"])
@use_args_with(UserProjectsGetParams)
def get_project_users_detail(reqargs):
    projectUUID = reqargs["projectId"]
    project_id = ProjectModel.get_project_id_for_uuid(projectUUID[0])

    if project_id:
        res = jsonify(UsersProjects.get_project_users(project_id))
        return res
    return jsonify({"error": "No projects found for the user"})


@users_blueprint.route("/users/edit_email_valid/", methods=["POST"])
def edit_user_email_valid():
    if request.json:
        uuid = request.json["uuid"]

        UserModel.edit_email_valid(uuid)
        return jsonify({"result": True, "Edit": "successful"})

    else:
        return jsonify({"result": False, "error": "no information updated"})


@users_blueprint.route("/users/email_exists/", methods=["POST"])
def email_exists():
    if request.json:
        email = request.json["email_address"]
        res = UserModel.is_email_exists(email)
        return res

    return jsonify(
        {
            "successful": False,
            "message": "something went wrong please try again after some time",
        }
    )


@users_blueprint.route("/users/set_new_password/", methods=["POST"])
def set_new_password():
    if request.json:
        user_id = request.json["user_id"]
        password = request.json["password"]

        res = UserModel.update_password(user_id, password)
        return res

    return jsonify(
        {
            "success": False,
            "message": "something went wrong please try again after some time",
        }
    )


@users_blueprint.route("/users/all/", methods=["GET", "POST"])
def get_users_all():
    def execute():
        users = UserModel.get_all_users_for_dashboard()
        if users:
            all_users = [
                {
                    "uuid": str(user.uuid),
                    "auth_type": user.auth_type,
                    "display_name": user.display_name,
                    "email_valid": user.email_valid,
                    "email_address": user.email_address,
                    "role": user.roles[0].name,
                }
                for user in users
            ]
            return jsonify(all_users)
        else:
            return jsonify({"error": "Something went wrong"})

    return execute()


@users_blueprint.route("/project/unregisterUser/", methods=["GET"])
def delete_user_from_project():
    if request.json:
        projectUUID = request.json["projectUUID"]
        userUUID = request.json["userUUID"]
        userRemoved = UsersProjects.delete_user_from_project(projectUUID, userUUID)
        return userRemoved
    return jsonify({"result": "Failed"})


@users_blueprint.route("/user/doesUserExist/", methods=["GET"])
@use_args_with(UserEmailArgs)
def is_email_exist(reqargs):
    emailId = reqargs["emailId"]
    if emailId:
        doesEmailExist = UserModel.is_email_exists(emailId)
        return doesEmailExist
    return jsonify({"result": "Failed"})


@users_blueprint.route("/project/addUser/", methods=["GET"])
def add_user_to_project():
    if request.json:
        projectUUID = request.json["projectUUID"]
        userUUID = request.json["userUUID"]
        userAdded = UsersProjects.add_user_to_project(projectUUID, userUUID)
        return jsonify(userAdded)
    return jsonify({"result": "Failed"})


@users_blueprint.route("/users/getAllSystemAdmin/", methods=["GET"])
def get_all_system_admin():
    return UserModel.get_All_System_Admin()
