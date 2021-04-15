from extensions import db
from ._base import ModelMixin


class OntologyArchiveModel(db.Model, ModelMixin):
    __tablename__ = "ontology_archive_table"

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid_entry = db.Column('uuid_entry', db.String)
    name = db.Column('ontology_name', db.String)
    lookup_type = db.Column('ontology_lookup_type', db.String)
    access_type = db.Column('ontology_access_type', db.String)
    lookup_path = db.Column('ontology_lookup_path', db.String)
    # using database entries for now.
    ontology_data = db.Column('ontology_data', db.String)

    # access_rights = db.Column('ontology_lookup_path', db.String)
    # we need some mechanism to determine who can access it (persons / groups)

    def __init__(self, name, lookup_type, access_type, lookup_path, uuid_entry, ontology_data):
        self.name = name
        self.ontology_lookup_type = lookup_type
        self.ontology_access_type = access_type
        self.ontology_lookup_path = lookup_path
        self.uuid_entry = uuid_entry
        self.ontology_data = ontology_data

    @classmethod
    def create_new_ontology_data_entry(cls, name, lookup_type, access_type, path_to_data, uuid_entry, content):
        if lookup_type == 'local' and path_to_data == 'internal' and access_type == 'public' and content:
            # -- create the table entry
            new_entry = OntologyArchiveModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                             lookup_path=path_to_data, uuid_entry=uuid_entry, ontology_data=content)

            db.session.add(new_entry)
            db.session.commit()

        if lookup_type == 'online' and access_type == "public":
            data = cls.integrate_new_ontology_data(path_to_data)
            # we are using the db table entry to store the ontology data.
            # TODO WE need to encrypt it before adding it to the data entry.

            # -- create the table entry
            new_entry = OntologyArchiveModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                             lookup_path=path_to_data, uuid_entry=uuid_entry, ontology_data=data)
            db.session.add(new_entry)
            db.session.commit()

    @classmethod
    def integrate_new_ontology_data(cls, url):
        print("want to lookup the ontology data: ", url, flush=True)
        return "This is our data Blog, Hello Ontology"

    @classmethod
    def get_ontology_from_archive(cls, ontology_id):
        return OntologyArchiveModel.query.filter_by(uuid_entry=ontology_id).first()

    @classmethod
    def get_all_ontology_from_archive(cls, ontology_id):
        return OntologyArchiveModel.query.all()
