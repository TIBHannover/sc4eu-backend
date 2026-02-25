from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)


user = os.environ.get("POSTGRES_USER")
passwd = os.environ.get("POSTGRES_PASSWORD")
db_postgres = os.environ.get("POSTGRES_DB")
CONTAINER = os.environ["CONTAINER_NAME"]

engine = create_engine(
    f"postgresql+psycopg2://{user}:{passwd}@{CONTAINER}:5432/{db_postgres}"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
