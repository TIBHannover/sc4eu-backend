from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView

from util import use_args_with
from ._params import OntologyIndexingGetParams, UserHeaderGetParams, UploadOntologyGetParams, DeleteOntologyGetParams, \
    CreateProjectGetParams, NewProjectGetParams, DeleteProjectGetParams, EditProjectGeParams, GetOntologyGitDataGetParams
from models import OntologyIndexingModel, OntologyArchiveModel, UserModel, ProjectModel, UsersProjects
from functools import wraps
import json


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


class AllowsUpload(MethodView):
    @use_args_with(UserHeaderGetParams)
    def get(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        allowed_roles = ["Admin", "System Admin", "Project Admin", "Member"]

        @requires_role(allowed_roles, user_id, token)
        def execute():
            return jsonify({"result": True})

        return execute()


class UploadOntology(MethodView):
    @use_args_with(UploadOntologyGetParams)
    def post(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        #         print(user_id)
        #         print(token)
        #         print(request.json)
        data_item = request.json
        # >> 1) extract the parameters from req.json
        # > 2) figrure a way  to call the integrate_new_ontology function
        name = data_item['name']
        lookup_type = data_item['lookup_type']
        access_type = data_item['access_type']
        lookup_path = data_item['lookup_path']
        description = data_item['description']
        ontology_content = data_item['ontology_content']
        project_id = data_item['project_id']
        ontology_git_data = data_item['ontology_git_data']

        OntologyIndexingModel.integrate_new_ontology(name, lookup_type, access_type, lookup_path, description,
                                                     ontology_content, project_id, ontology_git_data)

        # >>> excute some code here I guess
        return jsonify({"result": True, "upload": 'successful'})


class OntologyIndexingAPI(MethodView):
    @use_args_with(OntologyIndexingGetParams)
    def get(self, reqargs):
        if reqargs.get("ontology_id"):
            archive_response = OntologyArchiveModel.get_ontology_from_archive(reqargs.get("ontology_id"))
            if archive_response:
                ontology = {"name": archive_response.name,
                            "ontology_data": archive_response.ontology_data, "uuid": archive_response.uuid_entry}
                return jsonify(ontology)
            else:
                return jsonify({'ontologyArchive': 'ERROR, Something went wrong :/ '})

        else:
            project_id = reqargs.get('project_id')
            index_response = OntologyIndexingModel.get_ontology_index(project_id)

            if len(index_response) == 0:
                return jsonify({'ontologyIndex': 'Undefined'})

            if index_response:
                all_ontologies = [{"name": ontology.name,
                                   # This could be redundant for the users >> investigate
                                   "uuid": ontology.uuid,
                                   "lookup_type": ontology.lookup_type,
                                   "access_type": ontology.access_type,
                                   "lookup_path": ontology.lookup_path,
                                   "description": ontology.description,
                                   "project_id": project_id} for ontology in index_response]
                return jsonify(all_ontologies)
            else:
                return jsonify({'ontologyIndex': 'ERROR'})

    def post(self):
        call = json.dumps(request.json)
        data_item = json.loads(call)
        name = data_item['name']
        lookup_type = data_item['lookup_type']
        access_type = data_item['access_type']
        lookup_path = data_item['lookup_path']
        description = data_item['description']
        ontology_content = data_item['ontology_content']
        project_id = data_item['project_id']
        ontology_git_data = data_item['ontology_git_data']
        OntologyIndexingModel.integrate_new_ontology(name, lookup_type, access_type, lookup_path, description,
                                                     ontology_content, project_id, ontology_git_data)
        return jsonify({'success': True})


class GetOntologyGitData(MethodView):
    @use_args_with(GetOntologyGitDataGetParams)
    def get(self, reqargs):
        ontology_id = reqargs.get("ontology_id")

        if ontology_id:
            res = jsonify(OntologyArchiveModel.get_ontology_git_Data(ontology_id))
            return res
        else:
            return {
                "success": False,
                "error": "No git data found"
            }


class DeleteOntology(MethodView):
    @use_args_with(DeleteOntologyGetParams)
    #     @use_args_with(UploadOntologyGetParams)
    def post(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")
        if user_id:
            # delete ontology
            call = json.dumps(request.json)
            data_item = json.loads(call)
            ontology_id = data_item['ontologyIdToDelete']
            # >> TODO : check if allowed
            OntologyIndexingModel.delete_ontology_index(ontology_id)

        return jsonify({'success': True})


class CreateNewProject(MethodView):
    @use_args_with(NewProjectGetParams)
    def post(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        project_item = request.json
        # >> 1) extract the parameters from req.json
        # > 2) figrure a way  to call the integrate_new_ontology function
        name = project_item['name']
        description = project_item['description']
        access_type = project_item['accessType']
        created_by = project_item['createdBy']

        project_id = ProjectModel.create_new_project(name, description, access_type,
                                                     created_by)
        if not project_id:
            return jsonify({"result": False, "message": "Project name already exists, Please use any other name"})

        user_Id = UserModel.get_user_id_for_uuid(user_id)

        UsersProjects.add_user_project(user_Id, project_id)
        # >>> excute some code here I guess
        return jsonify({"result": True, "creation": 'successful'})


class CreateProjectAPI(MethodView):
    @use_args_with(CreateProjectGetParams)
    def get(self, reqargs):
        project_response = ProjectModel.get_all_projects()
        if project_response:
            all_projects = [{"name": project.name,
                             # This could be redundant for the users >> investigate
                             "uuid": project.uuid,
                             "description": project.description,
                             "access_type": project.access_type,
                             "created_by": project.created_by, } for project in project_response]
            return jsonify(all_projects)
        else:
            return jsonify({'projects': 'ERROR'})

    def post(self, reqargs):
        user_id = reqargs.get("userId")
        call = json.dumps(request.json)
        project_item = json.loads(call)
        name = project_item['name']
        description = project_item['description']
        access_type = project_item['access_type']
        created_by = project_item['created_by']

        project_id = ProjectModel.create_new_project(name, description, access_type,
                                                     created_by)

        if not project_id:
            return jsonify({"result": False, "message": "Project name already exists, Please use any other name"})

        user_Id = UserModel.get_user_id_for_uuid(user_id)

        UsersProjects.add_user_project(user_Id, project_id)

        return jsonify({'success': True})


class EditProject(MethodView):
    @use_args_with(EditProjectGeParams)
    def post(self, reqargs):

        if request.json:
            uuid = request.json["uuid"]
            name = request.json["projectName"]
            description = request.json["projectDescription"]
            access_type = request.json["accessType"]

            ProjectModel.edit_project(uuid, name, description, access_type)
            return jsonify({"result": True, "Edit": 'successful'})

        else:
            return jsonify({"result": False, "error": "no information updated"})


class DeleteProject(MethodView):
    @use_args_with(DeleteProjectGetParams)
    def post(self, reqargs):
        project_id = reqargs.get("userId")
        token = reqargs.get("token")
        if project_id:
            # delete project
            call = json.dumps(request.json)
            project_item = json.loads(call)
            project_id = project_item['projectIdToDelete']
            # >> TODO : check if allowed
            ProjectModel.delete_project(project_id)
            return jsonify({'success': True})
        return jsonify({'DeleteProject': 'ERROR'})