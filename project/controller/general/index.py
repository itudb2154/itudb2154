from project import app
from flask import render_template, redirect, url_for, session, request

from project.models.database import *
from project.models.recipe import *

db = Database(app.config['DATABASE_URL'])

@app.route('/', methods = ['GET', 'POST'])
def index():

    role_id = session.get("role_id")
    if request.method == 'POST' and request.form['button'] == "search":
        recipes = db.getRecipesByName(request.form['searchValue'])
    else:
        recipes = db.getRecipes(-1)

    user = session.get("id")

    return render_template('index.html', recipes=recipes, user=user, role_id=role_id)