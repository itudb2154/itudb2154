
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

@app.route('/menu/add', methods = ['GET', 'POST'])
@login_required
def addMenu():
    role_id = session.get("role_id")
    if request.method == 'POST':
        if request.form['addMenu'] == "insertValue":
            menuTitle = request.form['title']
            menuDescription = request.form['description']
            menuNotes = request.form['notes']
            userMeals = request.form.getlist('meal')
            dateNow = int(time.time())

            userMenu = Menu(menuTitle, menuDescription, dateNow, dateNow, menuNotes)

            menuId = db.addUserMenu(userMenu, session.get("id"))

            db.addUserMenuMeals(userMeals, menuId[0])

            url = "/user/" + str(session.get("id")) + "/menus"
            return redirect(url)

        elif request.form['addMenu'] == "addPage":
            meals = db.get_meals()
            return render_template('addmenu.html', meals=meals, user=session.get("id"), role_id=role_id)