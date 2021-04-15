# -*- coding: utf-8 -*-
from app_factory import create_app
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

app = create_app()
app.secret_key = 'development'




@app.route('/')
def index():
    return "Ontology Data Infrastructure"


if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'])
