from project import app
from flask import render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from project.models.database import *
from project.models.recipe import *
import time
import datetime  

db = Database("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16")

app.config['SECRET_KEY'] = 'thisisthesecret'

#db connection
import psycopg2
import requests

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16",sslmode = 'require')
cursor = connection.cursor()
#db connection complete

#session wrap
from functools import wraps
from flask import flash

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("id")
        if user_id:
            return func(*args, **kwargs)
            
        else:
            return redirect("/")
    return wrapper
#session wrap done


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if session.get("id"):
        return redirect("/")

    error = False
    if request.method == 'POST':
        #it returns the data

        #crpytion
        import hashlib
        # encode string "hello" to bytes
        plaintext = request.form['password'].encode()
        # call the sha256(...) function returns a hash object
        d = hashlib.sha256(plaintext)
        # generate binary hash of "hello" string
        hash = d.hexdigest()
        #crpytion complete

        #db selection test
        cursor.execute('''SELECT id FROM "user" where mail='%s' and password='%s';''' % (request.form['email'], hash))
        response = cursor.fetchone()
 
        if response == None:
            error = True
        else:
            session["id"] = response[0]
            return redirect("/")

    return render_template('login.html', error=error)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if session.get("id"):
        return redirect("/")

    if request.method == 'POST':
        #crpytion
        import hashlib
        # encode string "hello" to bytes
        plaintext = request.form['password'].encode()
        # call the sha256(...) function returns a hash object
        d = hashlib.sha256(plaintext)
        # generate binary hash of "hello" string
        hash = d.hexdigest()
        #crpytion complete

        cursor.execute('''SELECT id FROM "user" where mail='%s';''' % (request.form['email']))
        response = cursor.fetchone()
        if response != None:
            return render_template('register.html', error=True)
        #db insertion test
        cursor.execute('''INSERT INTO "user" (name, password, mail, country_id) VALUES ('%s', '%s', '%s', (select id from country where name='adminLand')) ON CONFLICT DO NOTHING;''' % (request.form['name'], hash, request.form['email']))
        
        connection.commit()

        cursor.execute('''SELECT * FROM "user";''')
        print(cursor.fetchall())
        success = True
        return render_template('register.html', success=True),  {"Refresh": "2; url=/login"}

    return render_template('register.html')


@app.route('/', methods = ['GET', 'POST'])
def index():
    owner = -1
    recipes = db.getRecipes(-1)
    user = False
    if session.get("id"):
        user = True
        owner = session.get("id")

    return render_template('index.html', recipes=recipes, user=user, owner=owner)

@app.route('/menus', methods = ['GET', 'POST'])
@login_required
def menus():
    
    userMenus = db.getUserMenus(session.get("id"))
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

    return render_template('menus.html', user=True, userMenus=userMenus)

    
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if session.get("id"):
        session["id"] = None
        
    return redirect("/")

@app.route('/addrecipe', methods = ['GET', 'POST'])
@login_required
def addrecipe():
    if request.method == 'POST':
        #assuming the recipe is given correctly
        print(request.form['meal'])
        recipe = Recipe(max(session["id"]), request.form['name'], request.form['meal'], " ", request.form['instruction'], request.form['portion'], request.form['drink_alternate'], request.form['video_url'])
        recipeId = db.add_recipe(recipe)
        
        ingredients = request.form.getlist('ingredient')
        measures = request.form.getlist('measure')

        db.addRecipeIngredient(ingredients, measures, recipeId)
        
        return redirect("/")

    meals = db.get_meals()
    ingredients = db.getIngredients()

    return render_template('addrecipe.html', meals=meals, ingredients=ingredients, user=True)


@app.route('/menu/add', methods = ['GET', 'POST'])
@login_required
def addMenu():
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

            return redirect("/menus")

        elif request.form['addMenu'] == "addPage":
            meals = db.get_meals()
            return render_template('addmenu.html', meals=meals, user=True)

@app.route('/myrecipes', methods = ['GET', 'POST'])
@login_required
def myRecipes():
    recipes = db.getRecipes(session.get("id"))

    return render_template('recipes.html', recipes=recipes, user=True)