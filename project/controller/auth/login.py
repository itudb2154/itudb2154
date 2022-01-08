from project import app
from flask import render_template, redirect, url_for, session, request
from project.models.database import *
from project.models.recipe import *
import hashlib

from functools import wraps
db = Database("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16")

app.config['SECRET_KEY'] = 'thisisthesecret'

import psycopg2
import requests

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16",sslmode = 'require')
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
        cursor.execute('''SELECT id, role_id FROM users where mail='%s' and password='%s';''', (request.form['email'], hash))
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













    

