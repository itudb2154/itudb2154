import psycopg2
from .recipe import Recipe
class Database:
    def __init__(self, conn):
        self.conn = conn

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