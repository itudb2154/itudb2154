from project import app
from flask import render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from project.models.database import *
from project.models.recipe import *

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
            session["id"] = response
            return redirect("/")

    return render_template('login.html', error=error)

@app.route('/register', methods = ['GET', 'POST'])
def register():
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

    recipes = db.get_recipes()
    user = False
    if session.get("id"):
        user = True

    return render_template('index.html', recipes=recipes, user=user)

@app.route('/menus', methods = ['GET', 'POST'])
@login_required
def menus():
    #user = User()
    cursor.execute('''SELECT name FROM "user" where id='%s';''' % (session.get("id")))
    connection.commit()
    name = cursor.fetchone()
    return render_template('menus.html', name=name, user=True)

    
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
        db.add_recipe(recipe)

        return redirect("/")

    meals = db.get_meals()

    return render_template('addrecipe.html', meals=meals)