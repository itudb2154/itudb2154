from project import app
from flask import render_template, redirect, session, request

from project.models.database import *
from project.models.recipe import *

db = Database(app.config['DATABASE_URL'])

connection = psycopg2.connect(app.config['DATABASE_URL'], sslmode = 'require')
cursor = connection.cursor()

@app.route('/register', methods = ['GET', 'POST'])
def register():
    role_id = session.get("role_id")
    countries = db.getAllCountries();
    if session.get("id"):
        return redirect("/")

    if request.method == 'POST':
        import hashlib
        plaintext = request.form['password'].encode()
        d = hashlib.sha256(plaintext)
        hash = d.hexdigest()
        query = '''SELECT id FROM users where mail=%s;'''
        cursor.execute(query, [request.form['email']])
        response = cursor.fetchone()
        if response != None:
            return render_template('register.html', error=True)
        query = '''INSERT INTO users (name, surname, password, mail, country_id, age, role_id) VALUES (%s, %s, %s, %s, %s, %s, 0) ON CONFLICT DO NOTHING;'''
        cursor.execute(query,(request.form['name'], request.form['surname'], hash, request.form['email'], request.form['country'], request.form['age']))
        
        connection.commit()

        return render_template('register.html', success=True, role_id=role_id),  {"Refresh": "2; url=/login"}

    return render_template('register.html', countries=countries, role_id=role_id)