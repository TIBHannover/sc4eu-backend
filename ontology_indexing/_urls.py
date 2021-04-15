from flask import Blueprint
from .views import OntologyIndexingAPI

ontology_indexing_blueprint = Blueprint("ontology_indexing", __name__)

ontology_indexing_blueprint.add_url_rule('/ontologyIndex/', view_func=OntologyIndexingAPI.as_view('ontology_indexing_view'),
                                         methods=['GET', 'POST'])
