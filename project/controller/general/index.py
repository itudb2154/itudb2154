from project import app
from flask import render_template, redirect, url_for, session, request

from project.models.database import *
from project.models.recipe import *

db = Database("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16")

app.config['SECRET_KEY'] = 'thisisthesecret'

@app.route('/', methods = ['GET', 'POST'])
def index():
    role_id = session.get("role_id")
    if request.method == 'POST' and request.form['button'] == "search":
        recipes = db.getRecipesByName(request.form['searchValue'])
    else:
        recipes = db.getRecipes(-1)

    user = session.get("id")

    return render_template('index.html', recipes=recipes, user=user, role_id=role_id)