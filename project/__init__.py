from flask import Flask
from flask_session import Session

#create app object
app = Flask("project")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#import all folders which have .py files
from project.api import *
from project.models import *
from project.controller import *


