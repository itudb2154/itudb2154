import psycopg2
from .recipe import *
from .meal import *
class Database:
    def __init__(self, conn):
        self.conn = conn

    def add_recipe(self, recipe):
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = '''insert into recipe (user_id, meal_id, name, instruction, portion, drink_alternate, video_url) values (%s, (select id from meal where (name='%s') ), '%s', '%s', '%s', '%s', '%s');''' % (recipe.user_id, recipe.meal_name, recipe.recipe_name, recipe.instruction, recipe.portion, recipe.drink_alternate, recipe.video_url)
            cursor.execute(query)
            connection.commit()

            query = 'SELECT * FROM recipe;'
            cursor.execute(query)
            connection.commit()
            result = cursor.fetchall()
            print(result)

    
    def get_recipes(self):
        recipes = []
        with psycopg2.connect(self.conn, sslmode='require') as connection:
            cursor = connection.cursor()
            query = 'select recipe.id, user_id, recipe.name, meal.name, photo_url, instruction, portion, drink_alternate, video_url from meal JOIN recipe ON (meal.id=recipe.meal_id);'
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