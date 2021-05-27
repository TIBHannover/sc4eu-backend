from flask import Blueprint
from .views import OntologyIndexingAPI, AllowsUpload

ontology_indexing_blueprint = Blueprint("ontology_indexing", __name__)

ontology_indexing_blueprint.add_url_rule('/ontologyIndex/',
                                         view_func=OntologyIndexingAPI.as_view('ontology_indexing_view'),
                                         methods=['GET', 'POST'])

ontology_indexing_blueprint.add_url_rule('/allows_upload/', view_func=AllowsUpload.as_view('allows_upload_view'),
                                         methods=['GET'])
