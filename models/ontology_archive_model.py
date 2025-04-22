from extensions import db
from ._base import ModelMixin


class OntologyArchiveModel(db.Model, ModelMixin):
    __tablename__ = 'ontology_archive_table'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    uuid_entry = db.Column('uuid_entry', db.String)
    name = db.Column('ontology_name', db.String)
    lookup_type = db.Column('ontology_lookup_type', db.String)
    access_type = db.Column('ontology_access_type', db.String)
    lookup_path = db.Column('ontology_lookup_path', db.String)
    # using database entries for now.
    ontology_data = db.Column('ontology_data', db.String)
    ontology_git_data = db.Column('ontology_git_data', db.PickleType)

    # access_rights = db.Column('ontology_lookup_path', db.String)
    # we need some mechanism to determine who can access it (persons / groups)

    def __init__(self, name, lookup_type, access_type, lookup_path, uuid_entry, ontology_data, ontology_git_data):
        self.name = name
        self.ontology_lookup_type = lookup_type
        self.ontology_access_type = access_type
        self.ontology_lookup_path = lookup_path
        self.uuid_entry = uuid_entry
        self.ontology_data = ontology_data
        self.ontology_git_data = ontology_git_data

    @classmethod
    def create_new_ontology_data_entry(cls, name, lookup_type, access_type, path_to_data, uuid_entry, content,
                                       ontology_git_data):
        if lookup_type == 'local' and path_to_data == 'internal' and access_type == 'public' and content:
            # -- create the table entry
            new_entry = OntologyArchiveModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                             lookup_path=path_to_data, uuid_entry=uuid_entry, ontology_data=content,
                                             ontology_git_data=ontology_git_data)

            db.session.add(new_entry)
            db.session.commit()
        # maybe not relevant right now , but later!
        if ((lookup_type == 'online' or lookup_type == 'online-gitlab') and access_type == "public"):
            data = cls.integrate_new_ontology_data(path_to_data)
            # we are using the db table entry to store the ontology data.
            # TODO WE need to encrypt it before adding it to the data entry.

            # -- create the table entry
            new_entry = OntologyArchiveModel(name=name, lookup_type=lookup_type, access_type=access_type,
                                             lookup_path=path_to_data, uuid_entry=uuid_entry, ontology_data=content,
                                             ontology_git_data=ontology_git_data)
            db.session.add(new_entry)
            db.session.commit()

    # @classmethod
    # def update_existing_ontology_data(cls, ontology_id, content, ontology_git_data):
    #     # Fetch the ontology entry by ID
    #     ontology_to_update = db.session.query(OntologyArchiveModel).filter_by(uuid_entry=ontology_id).first()

    #     if ontology_to_update:
    #         # Update only the provided fields
    #         if content is not None:
    #             ontology_to_update.ontology_data = content
    #         if ontology_git_data is not None:
    #             ontology_to_update.ontology_git_data = ontology_git_data

    #         # Commit the changes
    #         db.session.commit()
    #         return ontology_to_update
    #     else:
    #         # If the ontology with the given ID does not exist, return None
    #         return None
    
    @classmethod
    def update_existing_ontology_data(cls, ontology_id, content=None, ontology_git_data=None):
        """
        Updates the ontology entry with the given ID. Only non-None fields will be updated.

        Args:
            ontology_id: The unique identifier for the ontology.
            content: New content to update.
            ontology_git_data: New Git data to update.

        Returns:
            The updated ontology object, or None if not found.
        """
        ontology_entry = db.session.query(OntologyArchiveModel).filter_by(uuid_entry=ontology_id).first()

        if not ontology_entry:
            return None

        if content is not None:
            ontology_entry.ontology_data = content
        if ontology_git_data is not None:
            ontology_entry.ontology_git_data = ontology_git_data

        if content is not None or ontology_git_data is not None:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return ontology_entry
    
    @classmethod
    def integrate_new_ontology_data(cls, url):
        return "This is our data Blog, Hello Ontology"

    @classmethod
    def get_ontology_from_archive(cls, ontology_id):
        return OntologyArchiveModel.query.filter_by(uuid_entry=ontology_id).first()

    @classmethod
    def get_all_ontology_from_archive(cls, ontology_id):
        return OntologyArchiveModel.query.all()

    @classmethod
    def get_ontology_git_Data(cls, ontology_id):
        ontology_data = db.session.query(OntologyArchiveModel).filter_by(uuid_entry=ontology_id).first()
        return ontology_data.ontology_git_data

    @classmethod
    def delete_ontology_byID(cls, ontology_id):
        # check if threre is data for id
        ontology_to_delete_exists = db.session.query(OntologyArchiveModel.uuid_entry).filter_by(
            uuid_entry=ontology_id).first() is not None

        if ontology_to_delete_exists:
            to_delete_entry = db.session.query(OntologyArchiveModel).filter_by(uuid_entry=ontology_id).first()
            db.session.delete(to_delete_entry)
            db.session.commit()
