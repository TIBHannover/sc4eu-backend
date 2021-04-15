# Backend Database
We use flask and postgres for the backend database.

STATE: <b>experimental</b>

The database schema is not yet fully designed, thus we need to do some preparations before we can start the service.

# Preparations 

## Create or Adjust the .env file
We have the .env.example file which you can use to create the .env file
The .env file initializes environment variable for the service, such as the port the application is running on and 
the postgres variables.

You can use the provided script `initalizeEnv.sh` which will make a copy ot the .env.example as .env file (it checks if the file exisits, if so no copy will be made)

We have two modes when we want to work with this service

1) containerized: running `docker-compose up -d` which will use the container name and setup the database uri
2) local : This is intended to be used as development environment. running `python3 app.py` will lunch the service on the local machine. 

## Database preparation
### Initialize database
In order to initialize the database a postgres instance needs to be running.

Call `docker-compose up -d postgres_sc3_backend`

This will start the postgres process and allow us to initialize and migrate the database.

Initialize the database first with `flask db init`
 
Then migrate it with `flask db migrate` 

Possible error could be that the url for postgres can not be resolved. Make sure that the flag `CONTAINERIZED` is set to Flase,
 i.e., `CONTAINERIZED=False`
 
Additionally, it can happen that we receive : `ERROR [root] Error: Target database is not up to date.`

In this case run `flask db upgrade` 


# Starting service

a) containerized: running `docker-compose up -d` which will use the container name and setup the database uri

<b> Make sure the `CONTAINERIZED` flag is set to True </b>

When running in containerized mode: the docker container needs to be rebuild if we change the schema of the db 
ensure to migrate and upgrade these in the database. 
Otherwise it will copy the _migration folder and do the magic.


b) local : This is intended to be used as development environment. running `python3 app.py` will lunch the service on the local machine. 

<b> Make sure the `CONTAINERIZED` flag is set Flase </b>



# Setting up local development 

1) Clone this git repo.
2) run `sh initializeEnv.sh`
-> this will create the .env file
3) run `docker-compose up -d postgres_sc3_backend` -> this will initialize the postgres process for the database
4) run `flask db init`
5) run `flask db migrate`
6) run `flask db upgrade`
7) run `python app.py` or `python3 app.py`

Now you should be able to open your browser at http://localhost:5000/ and see just a message "Ontology Data Infrastructure"


  
 


