from flask import Flask
from flask_session import Session
from secret import returnUrl, returnSecret

app = Flask("project")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = returnSecret()
app.config['DATABASE_URL'] = returnUrl()

Session(app)

from project.api import *
from project.models import *
from project.controller import *

