from flask import Blueprint
from .views import UserAPIRegister, UserAPILogin, UserHeader, AdminDashboard, ViewProfile

users_blueprint = Blueprint("users", __name__)

users_blueprint.add_url_rule('/users/register/', view_func=UserAPIRegister.as_view('users_view'),
                             methods=['POST'])

users_blueprint.add_url_rule('/users/login/', view_func=UserAPILogin.as_view('users_login'),
                             methods=['POST'])

users_blueprint.add_url_rule('/users/header/', view_func=UserHeader.as_view('users_header'),
                             methods=['GET'])

users_blueprint.add_url_rule('/users/viewProfile/', view_func=ViewProfile.as_view('view_profile'),
                             methods=['GET', 'POST'])

users_blueprint.add_url_rule('/admin/dashboard/', view_func=AdminDashboard.as_view('admin_dashboard'),
                             methods=['GET', 'POST'])
