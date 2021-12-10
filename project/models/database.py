import psycopg2

from project.models.ingredient import Ingredient
from .recipe import *
from .meal import *
from .menu import *

class Database:
    def __init__(self, conn):
        self.conn = conn

    def add_recipe(self, recipe):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into recipe (user_id, meal_id, name, instruction, portion, drink_alternate, video_url) values (%s, (select id from meal where (name='%s') ), '%s', '%s', '%s', '%s', '%s');''' % (recipe.user_id, recipe.meal_name, recipe.recipe_name, recipe.instruction, recipe.portion, recipe.drink_alternate, recipe.video_url)
            cursor.execute(query)
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
                query = '''select recipe.id, user_id, recipe.name, meal.name, photo_url, instruction, portion, drink_alternate, video_url from meal JOIN recipe ON (meal.id=recipe.meal_id) where (user_id = '%s');''' % (userId)
            cursor.execute(query)
            connection.commit()
            recipesDb = cursor.fetchall()

            for recipe_id, user_id, recipe_name, meal_name, photo_url, instruction, portion, drink_alternate, video_url in recipesDb:
                recipe = Recipe(user_id, recipe_name, meal_name, photo_url, instruction, portion, drink_alternate, video_url)
                recipes.append((recipe_id, recipe))
            return recipes

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

    def getIngredients(self):
        ingredients = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select * from ingredient;'
            cursor.execute(query)
            connection.commit()
            ingredientsDB = cursor.fetchall()

            for recipeId, recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType in ingredientsDB:
                ingredient = Ingredient(recipeName, recipeProtein, recipeCalorie, recipeFat, recipeType)
                ingredients.append((recipeId, ingredient))
            return ingredients
    
    def addRecipeIngredient(self, ingredients, measures, recipeId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            for ingredient, measure in zip(ingredients, measures):
                query = '''insert into ingredients_of_meal (recipe_id, ingredient_id, measurement_quantity) values (%s, (select id from ingredient where (name='%s')), '%s');''' % (recipeId[0], ingredient, measure)
                cursor.execute(query)

            connection.commit()

    def getUserMenus(self, userId):
        menus = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''select id, title, description, created_date, updated_date, notes from "userMenu" where (user_id = '%s');''' % (userId)
            cursor.execute(query)
            connection.commit()

            menusDB = cursor.fetchall()

            for id, title, description, created_date, updated_date, notes in menusDB:
                userMenu = Menu(title, description, created_date, updated_date, notes)
                menus.append((id, userMenu))
            return menus

    def addUserMenu(self, userMenu, userId):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into "userMenu" (title, description, created_date, updated_date, notes, user_id) values ('%s', '%s', %s, %s, '%s', '%s');''' % (userMenu.title, userMenu.description, userMenu.created_date, userMenu.updated_date, userMenu.notes, userId)
            cursor.execute(query)
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
                query = '''select id from meal where (name = '%s');''' % (meal)
                cursor.execute(query)
                mealId = cursor.fetchone()
                query = '''insert into "menuContent" (menu_id, meal_id) values  (%s, %s);''' % (menuId, mealId[0])
                cursor.execute(query)
                connection.commit()

