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

def calculateTime(myDict):	
    dateNow = int(time.time())	
    for key, comment in myDict:	
        if comment.updated_date != None:	
            timePast = dateNow - comment.updated_date	
            days = timePast // 86400	
            hours = timePast // 3600 % 24	
            minutes = timePast // 60 % 60	
            seconds = timePast % 60	
            if days:	
                comment.updated_date = str(days) + " days ago"	
                continue	
            if hours:	
                comment.updated_date = str(hours) + " hours ago"	
                continue	
            if minutes:	
                comment.updated_date = str(minutes) + " minutes ago"	
                continue	
            if seconds:	
                comment.updated_date = str(seconds) + " seconds ago"	
                continue


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
    countries = db.getAllCountries();
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
        query = '''SELECT id FROM "user" where mail=%s;'''
        cursor.execute(query, [request.form['email']])
        response = cursor.fetchone()
        if response != None:
            return render_template('register.html', error=True)
        #db insertion test
        query = '''INSERT INTO "user" (name, surname, password, mail, country_id, age, role_id) VALUES (%s, %s, %s, %s, %s, %s, 0) ON CONFLICT DO NOTHING;'''
        cursor.execute(query,(request.form['name'], request.form['surname'], hash, request.form['email'], request.form['country'], request.form['age']))
        
        connection.commit()

        return render_template('register.html', success=True),  {"Refresh": "2; url=/login"}

    return render_template('register.html', countries=countries)


@app.route('/', methods = ['GET', 'POST'])
def index():
    recipes = db.getRecipes(-1)
    user = session.get("id")

    return render_template('index.html', recipes=recipes, user=user)

@app.route('/menus/<int:ownerId>', methods = ['GET', 'POST'])
@login_required
def menus(ownerId):
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

    return render_template('menus.html', user=user, userMenus=userMenus, owner=owner)

    
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
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
        recipe = Recipe(session["id"], request.form['name'], request.form['meal'], " ", request.form['instruction'], request.form['portion'], request.form['drink_alternate'], request.form['video_url'])
        recipeId = db.add_recipe(recipe)
        
        ingredients = request.form.getlist('ingredient')
        measures = request.form.getlist('measure')

        db.addRecipeIngredient(ingredients, measures, recipeId[0])
        
        return redirect(url_for('index'))

    meals = db.get_meals()
    ingredients = db.getIngredients()

    return render_template('addrecipe.html', meals=meals, ingredients=ingredients, user=session.get("id"))


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

            url = "/menus/" + str(session.get("id"))
            return redirect(url)

        elif request.form['addMenu'] == "addPage":
            meals = db.get_meals()
            return render_template('addmenu.html', meals=meals, user=session.get("id"))

@app.route('/user/<int:ownerId>/recipes', methods = ['GET', 'POST'])
@login_required
def recipes(ownerId):
    recipes = db.getRecipes(ownerId) #show the recipes of the owner, not user

    if request.method == 'POST':
        if request.form['button'] == "addRecipe" and ownerId == session.get("id"): #click the button only if you are the owner
            return redirect(url_for('addrecipe'))

    owner = ownerId
    user = session.get("id")
    #if session.get("id") == ownerId:
        #owner = True    #if i am the owner, i can change this page

    return render_template('recipes.html', recipes=recipes, user=user, owner=owner)

@app.route('/recipe/<int:recipeId>/addIng', methods = ['GET', 'POST'])
@login_required
def addIng(recipeId):
    user = session.get("id")
    recipe = db.getRecipe(recipeId)
    owner = recipe[1].user_id
    allingredients = db.getIngredients()

    if request.method == 'POST' and user==owner and request.form['button'] == "add":
        ingredients = request.form.getlist('ingredient')
        measures = request.form.getlist('measure')
        db.addRecipeIngredient(ingredients, measures, recipeId)
        url = "/recipe/" + str(recipeId)
        return redirect(url)
        
    return render_template('addIngredient.html', allingredients=allingredients, user=user, owner=owner)

@app.route('/menu/<int:menuId>/addMeal', methods = ['GET', 'POST'])
@login_required
def addMeal(menuId):
    user = session.get("id")
    owner = db.getMenuOwner(menuId)

    allMeals = db.get_meals()

    if request.method == 'POST' and user==owner and request.form['button'] == "add":
        meals = request.form.getlist('meals')
        db.addUserMenuMeals(meals, menuId)
        url = "/menu/" + str(menuId)
        return redirect(url)

    return render_template('addMeal.html', allMeals=allMeals, user=user, owner=owner)

@app.route('/recipe/<int:recipeId>', methods = ['GET', 'POST'])	
@login_required	
def recipe(recipeId):	
    	
    user=session.get("id")	
    comments = db.getComments(recipeId)	
    recipe = db.getRecipe(recipeId)	
    ingredients = db.getIngredientsOfARecipe(recipeId)	
    owner = recipe[1].user_id	
    allingredients = db.getIngredients()	
    #change the created date 	
    dateNow = int(time.time())	
    for key, comment in comments:	
        timePast = dateNow - comment.created_date	
        days = timePast // 86400	
        hours = timePast // 3600 % 24	
        minutes = timePast // 60 % 60	
        seconds = timePast % 60	
        if days:	
            comment.created_date = str(days) + " days ago"	
            continue	
        if hours:	
            comment.created_date = str(hours) + " hours ago"	
            continue	
        if minutes:	
            comment.created_date = str(minutes) + " minutes ago"	
            continue	
        if seconds:	
            comment.created_date = str(seconds) + " seconds ago"	
            continue	
    calculateTime(comments)	
    #change the created date completed	
    if request.method == 'POST':	
        if request.form['button'] == "deleteRecipe":	
            if user==owner:	
                db.deleteRecipe(recipeId)	
                url = "/user/" + str(owner) + "/recipes"	
                return redirect(url)	
            return	
        elif request.form['button'] == "deleteIng":	
            if user==owner:	
                for key, value in request.form.items():	
                    if(value != "deleteIng"):	
                        db.deleteIngredient(value)	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)	
            return	
        elif request.form['button'] == "updateIng":	
            if user==owner:	
                myDict = []	
                for key, value in request.form.items():	
                    if(value != "updateIng"):	
                        myDict.append((key, value))	
                	
                db.updateIngredientOfMeals(myDict)	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)	
                	
            return 	
        elif request.form['button'] == "comment":	
            #the user in the session is making a comment	
            #created date 	
            dateNow = int(time.time())	
            #created date done	
            comment = Comment(user, recipeId, request.form['message'], dateNow, None, request.form['color'], request.form['language'], None)	
            db.addComment(comment)	
            comments = db.getComments(recipeId) #get new comments	
            url = "/recipe/" + str(recipeId)	
            return redirect(url)	
        elif request.form['button'] == "updateComment":	
            #the user in the session is updating a comment	
            comment = db.getComment(request.form['comment_id'])	
            if user==comment[0][1].user_id:	
                myDict = []	
                for key, value in request.form.items():	
                    if(value != "updateComment"):	
                        myDict.append((key, value))	
                	
                dateNow = int(time.time())	
                myDict.append(("updated_date", dateNow))	
                db.updateComment(myDict)	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)	
        elif request.form['button'] == "delete-comment":	
            comment = db.getComment(request.form['comment_id'])	
            if user==comment[0][1].user_id:	
                db.deleteComment(request.form['id2delete'])	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)	
            	
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, user=user, owner=owner, comments=comments, allingredients=allingredients)

@app.route('/menu/<int:menuId>', methods = ['GET', 'POST'])
@login_required
def menu(menuId):
    owner = db.getMenuOwner(menuId)
    user=session.get("id")

    menu = db.getMenu(menuId)
    meals = db.getMenuContents(menuId)
    allMeals = db.get_meals()

    if request.method == 'POST':
        if request.form.get('button') == "view":
            #only show contents, dont edit
            return render_template("menu.html", menu=menu, user=user, owner=owner, meals=meals, allMeals=allMeals)

        elif request.form.get('button') == "updateMeal":

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

    return render_template('menu.html', menu=menu, user=user, owner=owner, meals=meals, allMeals=allMeals)

@app.route('/user/<int:userId>', methods = ['GET', 'POST'])
def user(userId):
    user = session.get("id")      #current user in the session
    owner = db.getUser(userId)  #owner of the current page

    isOwner = (user == userId)

    if request.method == 'POST' and request.form.get('button') == "change-user" and isOwner:
        myDict = []
        for key, value in request.form.items():
            if(value != "change-user"):
                myDict.append((key, value))
                #myDict[i].value galiba
        
        owner = db.updateUser(myDict, userId)

    countries = db.getAllCountries()
    

    return render_template("user.html", user=user, owner=owner, isOwner=isOwner, countries=countries)


@app.route('/adminPanel', methods = ['GET', 'POST'])
@login_required
def admin():
    userid = session.get("id")      #current user in the session
    
    if request.method == 'POST' and request.form.get('delete-user'):
        id2delete = request.form['delete-user']
        db.deleteUser(id2delete)
        return redirect("/adminPanel?user=true")

    elif request.method == 'POST' and request.form.get('delete-meal'):
        id2delete = request.form['delete-meal']
        db.deleteMeal(id2delete)
        return redirect("/adminPanel?meal=true")
    
    elif request.method == 'POST' and request.form.get('button') == "update":
        db.updateMeal(request.form['key'],request.form['name'], request.form['photo_url'], request.form['coisine_name'], request.form['country_name'], request.form['category_name'])
        return redirect("/adminPanel?meal=true")

    user = request.args.get('user')
    meal = request.args.get('meal')

    edit = request.args.get('edit')

    if edit != None and edit.lower() == 'meal' and meal != None:
        editMeal = db.getMealbyId(meal)
        countries = db.getAllCountries();
        categories = db.getAllCategories();
        return render_template("editMealPage.html", user=userid, editMeal=editMeal, countries=countries, categories=categories, mealid=meal)


    if user != None and user.lower() == "true" :
        allUsers = db.getAllUsers()
        return render_template("adminPanel.html", user=userid, allUsers=allUsers, userSelected=True)
    if meal != None and meal.lower() == "true" :
        allMeals = db.get_meals()
        return render_template("adminPanel.html", user=userid, allMeals=allMeals, mealSelected=True)
    
    return render_template("adminPanel.html", user=userid)

    

