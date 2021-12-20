import psycopg2

from project.models.ingredient import Ingredient
from .recipe import *
from .meal import *
from .menu import *
from .user import *
from .comment import *

class Database:
    def __init__(self, conn):
        self.conn = conn

    def add_recipe(self, recipe):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into recipe (user_id, meal_id, name, instruction, portion, drink_alternate, video_url) values (%s, (select id from meal where (name=%s) ), %s, %s, %s, %s, %s);'''
            cursor.execute(query, (recipe.user_id, recipe.meal_name, recipe.recipe_name, recipe.instruction, recipe.portion, recipe.drink_alternate, recipe.video_url))
            connection.commit()

            query = 'SELECT id FROM recipe order by id desc;'
            cursor.execute(query)
            connection.commit()
            result = cursor.fetchone()
            print(result)
            return result

    
    def getRecipes(self, userId):
        recipes = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            if (userId == -1):
                query = 'select recipe.id, user_id, recipe.name, meal.name, photo_url, instruction, portion, drink_alternate, video_url from meal JOIN recipe ON (meal.id=recipe.meal_id);'
            else:
                query = '''select recipe.id, user_id, recipe.name, meal.name, photo_url, instruction, portion, drink_alternate, video_url from meal JOIN recipe ON (meal.id=recipe.meal_id) where (user_id = %s);'''
            cursor.execute(query, [userId])
            connection.commit()
            recipesDb = cursor.fetchall()

            for recipe_id, user_id, recipe_name, meal_name, photo_url, instruction, portion, drink_alternate, video_url in recipesDb:
                recipe = Recipe(user_id, recipe_name, meal_name, photo_url, instruction, portion, drink_alternate, video_url)
                recipes.append((recipe_id, recipe))
            return recipes

    def getRecipe(self, recipeId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select recipe.id, user_id, recipe.name, meal.name, photo_url, instruction, portion, drink_alternate, video_url from meal JOIN recipe ON (meal.id=recipe.meal_id) WHERE (recipe.id = %s);'
            
            cursor.execute(query, [recipeId])
            connection.commit()
            recipeDb = cursor.fetchone()
            
            recipeObject = Recipe(recipeDb[1], recipeDb[2], recipeDb[3], recipeDb[4], recipeDb[5], recipeDb[6], recipeDb[7], recipeDb[8])
            recipe = (recipeDb[0], recipeObject)
            return recipe

    def get_meals(self):
        meals = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select meal.id, meal.name, category.name, meal.photo_url, meal.coisine_name, meal.country_id from meal JOIN category ON (meal.category_id=category.id);'
            cursor.execute(query)
            connection.commit()
            mealsDb = cursor.fetchall()

            for meal_id, meal_name, category_name, photo_url, coisine_name, country_name in mealsDb:
                meal = Meal(meal_name, category_name, photo_url, coisine_name, country_name)
                meals.append((meal_id, meal))
            return meals

    def getIngredientsOfARecipe(self, key):
        ingredients = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select ingredients_of_meal.ingredient_id, ingredient.name, ingredient.protein, ingredient.calorie, ingredient.fat, ingredient.type, ingredients_of_meal.measurement_quantity from ingredients_of_meal JOIN ingredient ON ingredient.id = ingredients_of_meal.ingredient_id WHERE (recipe_id = %s);'
            cursor.execute(query, [key])
            connection.commit()
            ingredientsDB = cursor.fetchall()

            for ingredient_id, recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType, measurementQuantity in ingredientsDB:
                ingredient = Ingredient(recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType, measurementQuantity)
                ingredients.append((ingredient_id, ingredient))#be careful, ingredient_id is not unique, there might be multiple elements with different measurements
            return ingredients

    def getIngredients(self):
        ingredients = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select * from ingredient;'
            cursor.execute(query)
            connection.commit()
            ingredientsDB = cursor.fetchall()

            for recipeId, recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType in ingredientsDB:
                ingredient = Ingredient(recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType, 0)
                ingredients.append((recipeId, ingredient))
            return ingredients
    
    def addRecipeIngredient(self, ingredients, measures, recipeId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            for ingredient, measure in zip(ingredients, measures):
                query = '''insert into ingredients_of_meal (recipe_id, ingredient_id, measurement_quantity) values (%s, (select id from ingredient where (name=%s)), %s);'''
                cursor.execute(query, (recipeId[0], ingredient, measure))

            connection.commit()

    def getUserMenus(self, userId):
        menus = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''select id, title, description, created_date, updated_date, notes from "userMenu" where (user_id = %s);'''
            cursor.execute(query, [userId])
            connection.commit()

            menusDB = cursor.fetchall()

            for id, title, description, created_date, updated_date, notes in menusDB:
                userMenu = Menu(title, description, created_date, updated_date, notes)
                menus.append((id, userMenu))
            return menus

    def getMenu(self, menuId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select id, title, description, created_date, updated_date, notes from "userMenu" where (id = %s);'
            
            cursor.execute(query, [menuId])
            connection.commit()
            menuDb = cursor.fetchone()
            
            menuObject = Menu(menuDb[1], menuDb[2], menuDb[3], menuDb[4], menuDb[5])
            menu = (menuDb[0], menuObject)
            return menu

    def getMenuContents(self, key):
        meals = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select meal.id, meal.name, category.name, meal.photo_url, meal.coisine_name, country.name from meal JOIN "menuContent" on ("menuContent".meal_id = meal.id) JOIN country ON (country.id = meal.country_id) JOIN category ON (category.id = meal.category_id) WHERE ("menuContent".menu_id = %s)'
            cursor.execute(query, [key])
            connection.commit()
            mealsDB = cursor.fetchall()

            for mealId, mealName, mealCategoryName, mealPhotoUrl, mealCoisineName, mealCountryName in mealsDB:
                meal = Meal(mealName, mealCategoryName, mealPhotoUrl, mealCoisineName, mealCountryName) #not country name
                print(mealCategoryName)
                meals.append((mealId, meal))
            return meals

    def addUserMenu(self, userMenu, userId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into "userMenu" (title, description, created_date, updated_date, notes, user_id) values (%s, %s, %s, %s, %s, %s);'''
            cursor.execute(query, (userMenu.title, userMenu.description, userMenu.created_date, userMenu.updated_date, userMenu.notes, userId))
            connection.commit()

            query = 'SELECT id FROM "userMenu" order by id desc;'
            cursor.execute(query)
            connection.commit()
            menuId = cursor.fetchone()
            return menuId

    def addUserMenuMeals(self, userMeals, menuId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            for meal in userMeals:
                query = '''select id from meal where (name = %s);'''
                cursor.execute(query, [meal])
                mealId = cursor.fetchone()
                query = '''insert into "menuContent" (menu_id, meal_id) values  (%s, %s);'''
                cursor.execute(query, (menuId, mealId[0]))
                connection.commit()


    def getUser(self, userId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select "user".id, "user".name, "user".surname, "user".mail, "user".password, "user".age, country.name from "user" JOIN country ON ("user".country_id = country.id) where ("user".id = %s);'
            
            cursor.execute(query, [userId])
            connection.commit()
            userDb = cursor.fetchone()
            
            user = User(userDb[0], userDb[1], userDb[2], userDb[3], userDb[4], userDb[5], userDb[6])
            return user

    def addComment(self, comment):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into "comment" (user_id, recipe_id, message, created_date, updated_date, text_color, language) values (%s, %s, %s,TIMESTAMP %s, %s, %s, %s);'''
            cursor.execute(query, (comment.user_id, comment.recipe_id, comment.message, comment.created_date, comment.updated_date, comment.text_color, comment.language))
            connection.commit()

    def getComments(self, recipeId):
        comments = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select comment.id, comment.user_id, comment.message, comment.created_date, comment.updated_date, comment.text_color, comment.language, "user".name from comment JOIN "user" ON (comment.user_id = "user".id) WHERE ("comment".recipe_id = %s)'
            cursor.execute(query, [recipeId])
            connection.commit()
            commentsDb = cursor.fetchall()

            for commentId, user_id, message, created_date, updated_date, text_color, language, name in commentsDb:
                comment = Comment(user_id, recipeId, message, created_date, updated_date, text_color, language, name) 
                comments.append((commentId, comment))
            return comments

