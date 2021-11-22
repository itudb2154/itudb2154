from project import app
from flask import render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

app.config['SECRET_KEY'] = 'thisisthesecret'

#db connection
import psycopg2
import requests

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16",sslmode = 'require')
cursor = connection.cursor()
#db connection complete

bootstrap = Bootstrap(app)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
        #it returns the data

        #crpytion
        import hashlib
        # encode string "hello" to bytes
        plaintext = form.password.data.encode()
        # call the sha256(...) function returns a hash object
        d = hashlib.sha256(plaintext)
        # generate binary hash of "hello" string
        hash = d.hexdigest()
        #crpytion complete

        #db selection test
        cursor.execute('''SELECT id FROM "user" where mail='%s' and password='%s';''' % (form.username.data, hash))
        response = cursor.fetchone()
 
        if response == None:
            error = True;
        else:
            session["id"] = response;
            return redirect("/index")

    return render_template('login.html', form=form, error=error)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        #crpytion
        import hashlib
        # encode string "hello" to bytes
        plaintext = form.password.data.encode()
        # call the sha256(...) function returns a hash object
        d = hashlib.sha256(plaintext)
        # generate binary hash of "hello" string
        hash = d.hexdigest()
        #crpytion complete

        cursor.execute('''SELECT id FROM "user" where mail='%s';''' % (form.email.data))
        response = cursor.fetchone()
        if response != None:
            return render_template('register.html', form=form, error=True)
        #db insertion test
        cursor.execute('''INSERT INTO "user" (name, password, mail, country_id) VALUES ('%s', '%s', '%s', (select id from country where name='adminLand')) ON CONFLICT DO NOTHING;''' % (form.username.data, hash, form.email.data))
        
        connection.commit()

        cursor.execute('''SELECT * FROM "user";''')
        print(cursor.fetchall())
        success = True
        return render_template('register.html', form=form, success=True),  {"Refresh": "2; url=/login"}

    return render_template('register.html', form=form)


@app.route('/index', methods = ['GET', 'POST'])
def index():

    cursor.execute('''select meal.photo_url, recipe.instruction from meal JOIN recipe ON (meal.id= recipe.meal_id);''')
    connection.commit()
    recipes = cursor.fetchall()

    print(recipes[0][1])
    if not session.get("id"):
        return render_template('index.html', recipes=recipes, user=False)

    return render_template('index.html', recipes=recipes, user=True)

@app.route('/menus', methods = ['GET', 'POST'])
def menus():
    if session.get("id"):
        cursor.execute('''SELECT name FROM "user" where id='%s';''' % (session.get("id")))
        connection.commit()
        name = cursor.fetchone()
        return render_template('menus.html', name=name[0], user=True)
    
    return redirect("/index")

    
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if session.get("id"):
        session["id"] = None
        
    return redirect("/index")