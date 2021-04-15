from flask import jsonify, request, redirect, url_for, abort
from flask.views import MethodView

from util import use_args_with
from ._params import OntologyIndexingGetParams
from models import OntologyIndexingModel, OntologyArchiveModel

import json


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
