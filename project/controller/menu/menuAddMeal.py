
from project import app
from functools import wraps
from flask import render_template, redirect, session, request

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

@app.route('/menu/<int:menuId>/addMeal', methods = ['GET', 'POST'])
@login_required
def addMeal(menuId):
    role_id = session.get("role_id")
    user = session.get("id")
    owner = db.getMenuOwner(menuId)

    allMeals = db.get_meals()

    if request.method == 'POST' and user==owner and request.form['button'] == "add":
        meals = request.form.getlist('meals')
        db.addUserMenuMeals(meals, menuId)
        url = "/menu/" + str(menuId)
        return redirect(url)

    return render_template('addMeal.html', allMeals=allMeals, user=user, owner=owner, role_id=role_id)