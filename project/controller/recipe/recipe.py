
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


@app.route('/recipe/<int:recipeId>', methods = ['GET', 'POST'])	
@login_required	
def recipe(recipeId):	
    role_id = session.get("role_id")
    	
    user=session.get("id")	
    comments = db.getComments(recipeId)	
    recipe = db.getRecipe(recipeId)	
    ingredients = db.getIngredientsOfARecipe(recipeId)	
    owner = recipe[1].user_id	
    allingredients = db.getIngredients()
    allMeals = db.get_meals()
    meal = db.getMealbyName(recipe[1].meal_name)

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
            return redirect("/")

        elif request.form['button'] == "deleteIng":	
            if user==owner:	
                for key, value in request.form.items():	
                    if(value != "deleteIng"):	
                        db.deleteIngredientofRecipe(value)	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)
            return redirect("/")

        elif request.form['button'] == "updateIng":	
            if user==owner:	
                myDict = []	
                for key, value in request.form.items():	
                    if(value != "updateIng"):	
                        myDict.append((key, value))	
                	
                db.updateIngredientOfMeals(myDict)	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)	
            return redirect("/") 	

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
            return redirect("/")

        elif request.form['button'] == "delete-comment":	
            comment = db.getComment(request.form['comment_id'])	
            if user==comment[0][1].user_id:	
                db.deleteComment(request.form['id2delete'])	
                url = "/recipe/" + str(recipeId)	
                return redirect(url)
            return redirect("/")

        elif request.form['button'] == "submit-change":	
            if user==owner:
                myDict = []
                for key, value in request.form.items():
                    if(value != "submit-change"):
                        myDict.append((key, value))
                
                db.updateRecipe(myDict, recipeId)
     
                url = "/recipe/" + str(recipeId)
                return redirect(url)
            return redirect("/")
            	
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, user=user, owner=owner, comments=comments, allingredients=allingredients, role_id=role_id, allMeals=allMeals, meal=meal)

