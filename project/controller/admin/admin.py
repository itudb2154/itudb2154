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

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        role_id = session.get("role_id")
        if role_id == 1:
            return func(*args, **kwargs)
            
        else:
            return redirect("/")
    return wrapper

@app.route('/adminPanel', methods = ['GET', 'POST'])
@login_required
@admin_required
def admin():
    userid = session.get("id")
    role_id = session.get("role_id")
    
    if request.method == 'POST' and request.form.get('delete-user'):
        id2delete = request.form['delete-user']
        db.deleteUser(id2delete)
        return redirect("/adminPanel?user=true")

    elif request.method == 'POST' and request.form.get('delete-meal'):
        id2delete = request.form['delete-meal']
        db.deleteMeal(id2delete)
        return redirect("/adminPanel?meal=true")

    elif request.method == 'POST' and request.form.get('delete-ingredient'):
        id2delete = request.form['delete-ingredient']
        db.deleteIngredient(id2delete)
        return redirect("/adminPanel?ingredient=true")
    
    elif request.method == 'POST' and request.form.get('button') == "update":
        db.updateMeal(request.form['key'],request.form['name'], request.form['photo_url'], request.form['coisine_name'], request.form['country_name'], request.form['category_name'])
        return redirect("/adminPanel?meal=true")

    elif request.method == 'POST' and request.form.get('button') == "update-ingredient":
        db.updateIngredient(request.form['key'], request.form['name'], request.form['protein'], request.form['calorie'], request.form['fat'], request.form['ingType'])
        return redirect("/adminPanel?ingredient=true")

    elif request.method == 'POST' and request.form.get('button') == "addMeal":
        countries = db.getAllCountries()
        categories = db.getAllCategories()
        
        return render_template("addMealPage.html", user=userid, countries=countries, categories=categories, role_id=role_id)
        
    elif request.method == 'POST' and request.form.get('button') == "addIngredient":
        #when add ingredient button is clicked, we render addIngredientPage, choose its properties and return back to this route again
        return render_template("addIngredientPage.html", user=userid, role_id=role_id)
    
    elif request.method == 'POST' and request.form.get('button') == "submit-add":
        newMeal = Meal(request.form['name'], request.form['category_name'], request.form['photo_url'], request.form['coisine_name'], request.form['country_name'], )
        db.createMeal(newMeal)
        return redirect("/adminPanel?meal=true")

    elif request.method == 'POST' and request.form.get('button') == "submit-add-ingredient":
        newIngredient = Ingredient(0, request.form['name'], request.form['protein'], request.form['calorie'], request.form['fat'], request.form['ingType'], 0)
        db.createIngredient(newIngredient)
        return redirect("/adminPanel?ingredient=true")

    user = request.args.get('user')
    meal = request.args.get('meal')
    ingredient = request.args.get('ingredient')

    edit = request.args.get('edit')

    if edit != None and edit.lower() == 'meal' and meal != None:
        editMeal = db.getMealbyId(meal)
        countries = db.getAllCountries()
        categories = db.getAllCategories()
        return render_template("editMealPage.html", user=userid, editMeal=editMeal, countries=countries, categories=categories, mealid=meal, role_id=role_id)

    if edit != None and edit.lower() == 'ingredient' and ingredient != None:
        editIngredient = db.getIngredientbyId(ingredient)
        return render_template("editIngredientPage.html", user=userid, editIngredient=editIngredient, ingredientid=ingredient, role_id=role_id)

    if user != None and user.lower() == "true" :
        allUsers = db.getAllUsers()
        return render_template("adminPanel.html", user=userid, allUsers=allUsers, userSelected=True, role_id=role_id)
    if meal != None and meal.lower() == "true" :
        allMeals = db.get_meals()
        return render_template("adminPanel.html", user=userid, allMeals=allMeals, mealSelected=True, role_id=role_id)
    if ingredient != None and ingredient.lower() == "true" :
        allIngredients = db.getIngredients()
        return render_template("adminPanel.html", user=userid, allIngredients=allIngredients, ingredientSelected=True, role_id=role_id)
    
    
    return render_template("adminPanel.html", user=userid, role_id=role_id)

