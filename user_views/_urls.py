from flask import Blueprint
from .views import UserAPIRegister, UserAPILogin, UserHeader, AdminDashboard, ViewProfile, UserDelete, GetAllRoles, \
    UpdateUserRole, UpdateUserProjects, GetUserProjects, GetUserRole, EditEmailValid

users_blueprint = Blueprint("users", __name__)

users_blueprint.add_url_rule('/users/register/', view_func=UserAPIRegister.as_view('users_view'),
                             methods=['POST'])

users_blueprint.add_url_rule('/users/login/', view_func=UserAPILogin.as_view('users_login'),
                             methods=['POST'])

users_blueprint.add_url_rule('/edit/email_valid/', view_func=EditEmailValid.as_view('edit_user_email_valid'),
                             methods=['POST'])

users_blueprint.add_url_rule('/users/delete/', view_func=UserDelete.as_view('users_delete'),
                             methods=['GET'])
# TODO: change above methods to DELETE or POST

users_blueprint.add_url_rule('/users/header/', view_func=UserHeader.as_view('users_header'),
                             methods=['GET'])

users_blueprint.add_url_rule('/users/viewProfile/', view_func=ViewProfile.as_view('view_profile'),
                             methods=['GET', 'POST'])

users_blueprint.add_url_rule('/users/updateUserRole/', view_func=UpdateUserRole.as_view('update_user_role'),
                             methods=['POST'])

users_blueprint.add_url_rule('/admin/dashboard/', view_func=AdminDashboard.as_view('admin_dashboard'),
                             methods=['GET', 'POST'])

users_blueprint.add_url_rule('/roles/all/', view_func=GetAllRoles.as_view('roles'),
                             methods=['GET'])

users_blueprint.add_url_rule('/user/role/', view_func=GetUserRole.as_view('user_role'),
                             methods=['GET'])

users_blueprint.add_url_rule('/users/updateUserProjects/', view_func=UpdateUserProjects.as_view('update_user_projects'),
                             methods=['POST'])

users_blueprint.add_url_rule('/user/projects/', view_func=GetUserProjects.as_view('get_user_projects'),
                             methods=['GET'])
