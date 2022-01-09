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

@app.route('/user/<int:userId>', methods = ['GET', 'POST'])
def user(userId):
    role_id = session.get("role_id")
    user = session.get("id")      #current user in the session
    owner = db.getUser(userId)  #owner of the current page
    isOwner = (user == userId)
    countries = db.getAllCountries()

    if request.method == 'POST' and request.form.get('button') == "change-user" and isOwner:
        myList = []
        for key, value in request.form.items():
            if(value != "change-user"):
                myList.append((key, value))
                
        error = db.updateUser(myList, userId) # Can be used as error code******

        return render_template("user.html", user=user, owner=owner, isOwner=isOwner, countries=countries, role_id=role_id, error=error)
        
    return render_template("user.html", user=user, owner=owner, isOwner=isOwner, countries=countries, role_id=role_id, error=0)

@app.route('/user/<int:ownerId>/recipes', methods = ['GET', 'POST'])
@login_required
def recipes(ownerId):
    role_id = session.get("role_id")
    recipes = db.getRecipes(ownerId) #show the recipes of the owner, not user

    if request.method == 'POST':
        if request.form['button'] == "addRecipe" and ownerId == session.get("id"): #click the button only if you are the owner
            return redirect(url_for('addrecipe'))

    owner = ownerId
    user = session.get("id")

    return render_template('recipes.html', recipes=recipes, user=user, owner=owner, role_id=role_id)


@app.route('/user/<int:ownerId>/menus', methods = ['GET', 'POST'])
@login_required
def menus(ownerId):
    role_id = session.get("role_id")
    owner = ownerId
    user = session.get("id")
    userMenus = db.getUserMenus(owner)

    dateNow = int(time.time())

    for key, menu in userMenus:
        timePast = dateNow - menu.created_date

        days = timePast // 86400
        hours = timePast // 3600 % 24
        minutes = timePast // 60 % 60
        seconds = timePast % 60

        if days:
           menu.created_date = str(days) + " days ago"
           continue
        if hours:
           menu.created_date = str(hours) + " hours ago"
           continue
        if minutes:
           menu.created_date = str(minutes) + " minutes ago"
           continue
        if seconds:
           menu.created_date = str(seconds) + " seconds ago"
           continue

    return render_template('menus.html', user=user, userMenus=userMenus, owner=owner, role_id=role_id)
