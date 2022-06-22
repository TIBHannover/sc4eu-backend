# -*- coding: utf-8 -*-
from app_factory import create_app
from dotenv import load_dotenv

# testing user model find or create user
from models import UserModel
from models import Role
from models import ProjectModel
from models import OntologyIndexingModel

load_dotenv()  # take environment variables from .env.

app = create_app()
app.secret_key = 'development'


# Initializing the role models with default values

@app.route('/')
def index():
    return "Ontology Data Infrastructure"


if __name__ == "__main__":
    with app.app_context():
        Role.initialize()
        UserModel.initialize_admin_user()
        ProjectModel.initializeDefaultProject()
        OntologyIndexingModel.initializeDefaultData()
    app.run(host=app.config['HOST'], port=app.config['PORT'])
