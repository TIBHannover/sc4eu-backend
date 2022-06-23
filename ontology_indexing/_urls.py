from flask import Blueprint
from .views import OntologyIndexingAPI, AllowsUpload, UploadOntology, DeleteOntology
from .views import CreateProjectAPI, CreateNewProject, DeleteProject

ontology_indexing_blueprint = Blueprint("ontology_indexing", __name__)
project_blueprint = Blueprint("project", __name__)

project_blueprint.add_url_rule('/projectIndex/', view_func=CreateProjectAPI.as_view('project_indexing_view'),
                               methods=['GET', 'POST'])

project_blueprint.add_url_rule('/create_new_project/', view_func=CreateNewProject.as_view('create_new_project_view'),
                               methods=['POST'])

project_blueprint.add_url_rule('/delete_project/', view_func=DeleteProject.as_view('delete_project_view'),
                               methods=['POST'])

ontology_indexing_blueprint.add_url_rule('/ontologyIndex/',
                                         view_func=OntologyIndexingAPI.as_view('ontology_indexing_view'),
                                         methods=['GET', 'POST'])

ontology_indexing_blueprint.add_url_rule('/allows_upload/', view_func=AllowsUpload.as_view('allows_upload_view'),
                                         methods=['GET'])

ontology_indexing_blueprint.add_url_rule('/upload_ontology/', view_func=UploadOntology.as_view('upload_ontology_view'),
                                         methods=['POST'])

ontology_indexing_blueprint.add_url_rule('/delete_ontology/', view_func=DeleteOntology.as_view('delete_ontology_view'),
                                         methods=['POST'])

