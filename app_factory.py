# -*- coding: utf-8 -*-
from flask import make_response, jsonify
from util import ListConverter, NumpyEncoder
from flask_cors import CORS
from ontology_indexing import ontology_indexing_blueprint, project_blueprint
from user_views.views import users_blueprint
from extensions import db, migrate, app
import os
from distutils.util import strtobool

DEFAULT_BLUEPRINTS = [ontology_indexing_blueprint, users_blueprint, project_blueprint]


def create_app(blueprints=None):
    """
    Builds up a Flask app and return it to the caller
    :param blueprints: a custom list of Flask blueprints
    :return: Flask app object
    """
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    configure_app(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_error_handlers(app)
    configure_encryption(app)

    return app


def setup_sqlalchemy_uri(app_object):
    # BUILD SQLALCHEMY_DATA_BASE_URI
    uri = os.environ["SQLALCHEMY_DATABASE_URI"]
    user = os.environ["POSTGRES_USER"]
    passwd = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    containerized = os.environ["CONTAINERIZED"]
    container_name = os.environ["CONTAINER_NAME"]

    testing_env = bool(strtobool(os.getenv('TESTING_FLAG')))
    if testing_env:
        app_object.config[
            "SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{user}:{passwd}@localhost:5432/{db}"
    else:
        if not uri:
            domain = 'localhost'
            if containerized == "True":
                domain = container_name

            database_url = f'postgresql+psycopg2://{user}:{passwd}@{domain}:5432/{db}'
            app_object.config["SQLALCHEMY_DATABASE_URI"] = database_url

        else:
            app_object.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]

    print("Setup URI FOR DB:" + app_object.config["SQLALCHEMY_DATABASE_URI"])


def configure_app(app_object):
    app_object.url_map.converters['list'] = ListConverter
    app_object.json_encoder = NumpyEncoder

    setup_sqlalchemy_uri(app_object)

    # Set the modification tack flag
    # env variables are strings.
    track_modifications = os.environ["SQLALCHEMY_TRACK_MODIFICATIONS"]

    if track_modifications == "True":
        app_object.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    else:
        app_object.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # assign the HOST if we have the flags in env file, otherwise use 0.0.0.0
    app_object.config["HOST"] = os.environ[
        "DATA_INFRASTRUCTURE_FLASK_HOST"] if "DATA_INFRASTRUCTURE_FLASK_HOST" in os.environ else '0.0.0.0'

    # assign the PORT if we have the flags in env file, otherwise use 5000
    app_object.config["PORT"] = int(
        os.environ["DATA_INFRASTRUCTURE_FLASK_PORT"]) if "DATA_INFRASTRUCTURE_FLASK_PORT" in os.environ else 5000


def configure_blueprints(app_object, blueprints):
    for blueprint in blueprints:
        app_object.register_blueprint(blueprint)


def configure_extensions(app_obj):
    db.init_app(app_obj)
    migrate.init_app(app_obj, db, directory="_migrations", render_as_batch=True)
    CORS(app_obj)


def configure_encryption(app_obj):
    # TODO
    return


def configure_error_handlers(app_obj):
    @app_obj.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Page Not found'}), 404)

    # Return validation errors as JSON
    @app_obj.errorhandler(422)
    @app_obj.errorhandler(400)
    def handle_error(err):
        headers = err.data.get("headers", None)
        messages = err.data.get("messages", ["Invalid request."])
        if headers:
            return jsonify({"errors": messages}), err.code, headers
        else:
            return jsonify({"errors": messages}), err.code
