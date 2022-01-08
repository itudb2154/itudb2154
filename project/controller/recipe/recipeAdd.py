from project import app
from functools import wraps
from flask import render_template, redirect, url_for, session, request

from project.models.database import *
from project.models.recipe import *

db = Database("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16")

app.config['SECRET_KEY'] = 'thisisthesecret'

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("id")
        if user_id:
            return func(*args, **kwargs)
            
        else:
            return redirect("/")
    return wrapper
    
@app.route('/addrecipe', methods = ['GET', 'POST'])
@login_required
def addrecipe():
    role_id = session.get("role_id")
    if request.method == 'POST':
        #assuming the recipe is given correctly
        
        recipe = Recipe(session["id"], request.form['name'], request.form['meal'], " ", request.form['instruction'], request.form['portion'], request.form['drink_alternate'], request.form['video_url'])
        recipeId = db.add_recipe(recipe)
        
        ingredients = request.form.getlist('ingredient')
        measures = request.form.getlist('measure')

        db.addRecipeIngredient(ingredients, measures, recipeId[0])
        
        return redirect(url_for('index'))

    meals = db.get_meals()
    ingredients = db.getIngredients()

    return render_template('addrecipe.html', meals=meals, ingredients=ingredients, user=session.get("id"), role_id=role_id)