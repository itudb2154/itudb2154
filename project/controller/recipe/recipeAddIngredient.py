from project import app
from functools import wraps
from flask import render_template, redirect, url_for, session, request

from project.models.database import *
from project.models.recipe import *

db = Database(app.config['DATABASE_URL'])


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("id")
        if user_id:
            return func(*args, **kwargs)
            
        else:
            return redirect("/")
    return wrapper

@app.route('/recipe/<int:recipeId>/addIng', methods = ['GET', 'POST'])
@login_required
def addIng(recipeId):
    role_id = session.get("role_id")
    user = session.get("id")
    recipe = db.getRecipe(recipeId)
    owner = recipe[1].user_id
    if user != owner:
        return redirect("/")

    allingredients = db.getIngredients()

    if request.method == 'POST' and request.form['button'] == "add":
        ingredients = request.form.getlist('ingredient')
        measures = request.form.getlist('measure')
        db.addRecipeIngredient(ingredients, measures, recipeId)
        url = "/recipe/" + str(recipeId)
        return redirect(url)
        
    return render_template('addIngredient.html', allingredients=allingredients, user=user, owner=owner, role_id=role_id)