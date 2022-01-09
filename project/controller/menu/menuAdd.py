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

    meals = db.get_meals()
    return render_template('addmenu.html', meals=meals, user=session.get("id"), role_id=role_id)