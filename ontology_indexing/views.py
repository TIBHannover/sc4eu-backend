from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView

from util import use_args_with
from ._params import OntologyIndexingGetParams, UserHeaderGetParams, UploadOntologyGetParams, DeleteOntologyGetParams, \
    CreateProjectGetParams, NewProjectGetParams, DeleteProjectGetParams
from models import OntologyIndexingModel, OntologyArchiveModel, UserModel, ProjectModel
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
            print('trying to  get the user')
            print("user_id", outer_args[0])

            # check if user has role ???
            user_role = UserModel.get_user_role_for_id(outer_args[0])
            print(user_role)
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
        print("WE have some request in the backend to integrate new ontology", flush=True)
        data_item = request.json
        # >> 1) extract the parameters from req.json
        # > 2) figrure a way  to call the integrate_new_ontology function
        name = data_item['name']
        lookup_type = data_item['lookup_type']
        access_type = data_item['access_type']
        lookup_path = data_item['lookup_path']
        description = data_item['description']
        ontology_content = data_item['ontology_content']

        # 1) debug the extracted items
        print(lookup_type)
        print(access_type)
        print(lookup_path)
        print(description)
        print(ontology_content)

        print(data_item, flush=True)

        OntologyIndexingModel.integrate_new_ontology(name, lookup_type, access_type, lookup_path, description,
                                                     ontology_content)

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
            index_response = OntologyIndexingModel.get_ontology_index()

            if index_response:
                all_ontologies = [{"name": ontology.name,
                                   # This could be redundant for the users >> investigate
                                   "uuid": ontology.uuid,
                                   "lookup_type": ontology.lookup_type,
                                   "access_type": ontology.access_type,
                                   "lookup_path": ontology.lookup_path,
                                   "description": ontology.description} for ontology in index_response]
                return jsonify(all_ontologies)
            else:
                return jsonify({'ontologyIndex': 'ERROR'})

    def post(self):
        call = json.dumps(request.json)
        data_item = json.loads(call)
        print(data_item, flush=True)
        name = data_item['name']
        lookup_type = data_item['lookup_type']
        access_type = data_item['access_type']
        lookup_path = data_item['lookup_path']
        description = data_item['description']
        ontology_content = data_item['ontology_content']
        OntologyIndexingModel.integrate_new_ontology(name, lookup_type, access_type, lookup_path, description,
                                                     ontology_content)
        return jsonify({'success': True})


class DeleteOntology(MethodView):
    @use_args_with(DeleteOntologyGetParams)
    #     @use_args_with(UploadOntologyGetParams)
    def post(self, reqargs):
        print("Inside DeleteOntology backend")

        print(request.json)
        user_id = reqargs.get("userId")
        token = reqargs.get("token")
        print(user_id, flush=True)
        print(token, flush=True)
        if user_id:
            # delete ontology
            print("DB CALL TO DELTE ONTOLOGY")
            print('ontolgyID', reqargs.get("userID"), flush=True)
            call = json.dumps(request.json)
            data_item = json.loads(call)
            ontology_id = data_item['ontologyIdToDelete']
            print(">>>>>>>>>>>>>>>>>>>>", ontology_id, flush=True)
            # >> TODO : check if allowed
            OntologyIndexingModel.delete_ontology_index(ontology_id)

        return jsonify({'success': True})


class CreateNewProject(MethodView):
    @use_args_with(NewProjectGetParams)
    def post(self, reqargs):
        user_id = reqargs.get("userId")
        token = reqargs.get("token")

        print("WE have some request in the backend to create new project", flush=True)
        project_item = request.json
        print(project_item)
        # >> 1) extract the parameters from req.json
        # > 2) figrure a way  to call the integrate_new_ontology function
        name = project_item['name']
        description = project_item['description']
        created_by = project_item['createdBy']

        # 1) debug the extracted items
        print(name)
        print(description)
        print(created_by)

        print(project_item, flush=True)

        ProjectModel.create_new_project(name, description,
                                        created_by)

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
                             "created_by": project.created_by, } for project in project_response]
            return jsonify(all_projects)
        else:
            return jsonify({'projects': 'ERROR'})

    def post(self):
        call = json.dumps(request.json)
        project_item = json.loads(call)
        print(project_item, flush=True)
        name = project_item['name']
        description = project_item['description']
        created_by = project_item['created_by']

        # 1) debug the extracted items
        print(name)
        print(description)
        print(created_by)

        print(project_item, flush=True)

        ProjectModel.create_new_project(name, description,
                                        created_by)
        return jsonify({'success': True})


class DeleteProject(MethodView):
    @use_args_with(DeleteProjectGetParams)
    def post(self, reqargs):
        print("Inside DeleteProject backend")
        print(request.json)
        project_id = reqargs.get("userId")
        token = reqargs.get("token")
        print('who is deleting?', project_id, flush=True)
        print(token, flush=True)
        if project_id:
            # delete project
            print("DB CALL TO DELETE PROJECT")
            print('projectID', reqargs.get("projectIdToDelete"), flush=True)
            call = json.dumps(request.json)
            project_item = json.loads(call)
            project_id = project_item['projectIdToDelete']
            print(">>>>>>>>>>>>>>>>>>>>", project_id, flush=True)
            # >> TODO : check if allowed
            ProjectModel.delete_project(project_id)
            return jsonify({'success': True})
        return jsonify({'DeleteProject': 'ERROR'})
