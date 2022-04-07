# itudb2154
RecipesDBProject
varlike18
korkusuzc18

--------------------------------------------------
To run the project, type:

python3 server.py

into command line while using venv.
--------------------------------------------------

We use remote postgreSQL server provided from HerokuApp for free. For your information: it is little bit slow. Each connection takes approximately 1 seconds. 

You can define your local PostgreSQL-server connection string into initDatabase.py. It should also work. Also, if you change the connection string in secret.py, whole program will adapt to it except initDatabase.py.
