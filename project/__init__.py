from flask import Flask

#create app object
app = Flask("project")

#import all folders which have .py files
from project.api import *
from project.controller import *
from project.models import *
