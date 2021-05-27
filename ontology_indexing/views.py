from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView

from util import use_args_with
from ._params import OntologyIndexingGetParams, UserHeaderGetParams
from models import OntologyIndexingModel, OntologyArchiveModel, UserModel
from functools import wraps
import json


def requires_role(role_name, *outer_args, **outer_kwargs):
    def wrapper(view_function, *wrapper_args, **wrapper_kwargs):
        for x in wrapper_args:
            print("OuterAgs:" + x)

        for x in wrapper_kwargs.values():
            print("Outer KAgs:" + x)

        @wraps(view_function)  # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):
            # user_manager = current_app.user_manager
            print('trying to  get the user')
            print("role name", role_name)
            print("user_id", outer_args[0])

            # check if user has role ???
            user_role = UserModel.get_user_role_for_id(outer_args[0])
            print(user_role)
            if role_name == user_role:
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

        @requires_role("Admin", user_id, token)
        def execute():
            return jsonify({"result": True})

        return execute()


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
