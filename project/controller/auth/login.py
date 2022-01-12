from project import app
from flask import render_template, redirect, session, request
from project.models.database import *
from project.models.recipe import *
import hashlib
import psycopg2

from functools import wraps
db = Database(app.config['DATABASE_URL'])

connection = psycopg2.connect(app.config['DATABASE_URL'])
cursor = connection.cursor()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("id")
        if user_id:
            return func(*args, **kwargs)
            
        else:
            return redirect("/")
    return wrapper

@app.route('/login', methods = ['GET', 'POST'])
def login():
    role_id = session.get("role_id")
    if session.get("id"):
        return redirect("/")

    error = False
    if request.method == 'POST':
        
        plaintext = request.form['password'].encode()
        d = hashlib.sha256(plaintext)
        hash = d.hexdigest()
        query = "SELECT id, role_id FROM users where mail=%s and password=%s;"
        cursor.execute(query, (request.form['email'], hash))
        response = cursor.fetchone()
 
        if response == None:
            error = True
        else:
            session["id"] = response[0]
            session["role_id"] = response[1]
            return redirect("/")

    return render_template('login.html', error=error, role_id=role_id)


    
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():

    if session.get("id"):
        session["id"] = None
        session["role_id"] = None
        
    return redirect("/")













    

