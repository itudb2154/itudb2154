
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


@app.route('/menu/<int:menuId>', methods = ['GET', 'POST'])
@login_required
def menu(menuId):
    role_id = session.get("role_id")
    owner = db.getMenuOwner(menuId)
    user=session.get("id")

    menu = db.getMenu(menuId)
    meals = db.getMenuContents(menuId)
    allMeals = db.get_meals()

    if request.method == 'POST':
        if request.form.get('button') == "updateMeal":
            if user==owner:
                myDict = []
                for key, value in request.form.items():
                    if(value != "updateMeal"):
                        myDict.append((key, value))

                db.updateMenuContent(myDict)

                url = "/menu/" + str(menuId)
                return redirect(url)

        elif request.form.get('button') == "deleteMeal":
            if user==owner:
                for key, value in request.form.items():
                    if(value != "deleteMeal"):
                        db.deleteMenuContent(value)

                url = "/menu/" + str(menuId)
                return redirect(url)

        elif request.form.get('button') == "deleteMenu":
            if user==owner:
                db.deleteUserMenu(menuId)
                url = "/menus/" + str(owner)
                return redirect(url)
        
        elif request.form.get('button') == "submit-change":
            if user==owner:
                myDict = []
                for key, value in request.form.items():
                    if(value != "submit-change"):
                        myDict.append((key, value))

                db.updateUserMenu(myDict, menuId)
                url = "/menu/" + str(menuId)
                return redirect(url)

    return render_template('menu.html', menu=menu, user=user, owner=owner, meals=meals, allMeals=allMeals, role_id=role_id)