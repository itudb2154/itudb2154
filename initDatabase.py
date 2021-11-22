import psycopg2
import requests

TABLE_CREATE_QUERY = [
        '''CREATE TABLE IF NOT EXISTS "country" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(80) UNIQUE
        )''',

        '''CREATE TABLE IF NOT EXISTS "category" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(80) UNIQUE
            )''',

        '''CREATE TABLE IF NOT EXISTS "meal" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(50),
            "category_id" int,
            "photo_url" VARCHAR,
            "coisine_name" VARCHAR(50),
            "country_id" INTEGER NOT NULL
            )''',
 
        '''CREATE TABLE IF NOT EXISTS "user" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(80),
            "surname" VARCHAR(80),
            "mail" VARCHAR(80),
            "password" VARCHAR(80),
            "age" INTEGER,
            "country_id" INTEGER NOT NULL
            )''',
 
        '''CREATE TABLE IF NOT EXISTS "recipe" (
            "id" SERIAL PRIMARY KEY,
            "user_id" INTEGER NOT NULL,
            "meal_id" INTEGER NOT NULL,
            "name" VARCHAR(80) UNIQUE,
            "instruction" VARCHAR,
            "portion" VARCHAR(50),
            "drink_alternate" VARCHAR(50),
            "video_url" VARCHAR(80)
            )''',
    
        '''CREATE TABLE IF NOT EXISTS "ingredient" (
            "id" SERIAL PRIMARY KEY,
            "name" VARCHAR(50) UNIQUE,
            "protein" FLOAT,
            "calorie" FLOAT,
            "fat" FLOAT,
            "type" VARCHAR(50)
            )''',

        '''CREATE TABLE IF NOT EXISTS "comment" (
            "id" SERIAL PRIMARY KEY,
            "user_id" INTEGER NOT NULL,
            "recipe_id" INTEGER NOT NULL,
            "message" VARCHAR(200),
            "created_date" timestamp,
            "updated_date" timestamp,
            "text_color" VARCHAR(50),
            "language" VARCHAR(50)
            )''',

        '''CREATE TABLE IF NOT EXISTS "ingredients_of_meal" (
            "recipe_id" INTEGER NOT NULL,
            "ingredient_id" INTEGER NOT NULL,
            "measurement_quantity" VARCHAR(30)
            )''',

        '''CREATE TABLE IF NOT EXISTS"userMenu" (
            "id" SERIAL PRIMARY KEY,
            "title" VARCHAR(50),
            "description" VARCHAR,
            "created_date" timestamp,
            "updated_date" timestamp,
            "notes" VARCHAR,
            "user_id" int
            )''',

        '''CREATE TABLE IF NOT EXISTS "menuContent" (
            "menu_id" int,
            "meal_id" int
            )''',


        '''ALTER TABLE "meal" ADD FOREIGN KEY ("country_id") REFERENCES "country" ("id") ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE "meal" ADD FOREIGN KEY ("category_id") REFERENCES "category" ("id")''',

        '''ALTER TABLE "user" ADD FOREIGN KEY ("country_id") REFERENCES "country" ("id")''',

        '''ALTER TABLE "recipe" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id")''',

        '''ALTER TABLE "recipe" ADD FOREIGN KEY ("meal_id") REFERENCES "meal" ("id")''',

        '''ALTER TABLE "comment" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id")''',

        '''ALTER TABLE "comment" ADD FOREIGN KEY ("recipe_id") REFERENCES "recipe" ("id")''',

        '''ALTER TABLE "ingredients_of_meal" ADD FOREIGN KEY ("recipe_id") REFERENCES "recipe" ("id")''',

        '''ALTER TABLE "ingredients_of_meal" ADD FOREIGN KEY ("ingredient_id") REFERENCES "ingredient" ("id")''',

        '''ALTER TABLE "userMenu" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id")''',

        '''ALTER TABLE "menuContent" ADD FOREIGN KEY ("menu_id") REFERENCES "userMenu" ("id") ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE "menuContent" ADD FOREIGN KEY ("meal_id") REFERENCES "meal" ("id") ON DELETE CASCADE ON UPDATE CASCADE''',


]

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16",sslmode = 'require')
cursor = connection.cursor()

#deleting all the previous tables to recreate them
cursor.execute('''
                DROP TABLE IF EXISTS country cascade;
                DROP TABLE IF EXISTS category cascade;
                DROP TABLE IF EXISTS meal cascade;
                DROP TABLE IF EXISTS "user" cascade;
                DROP TABLE IF EXISTS recipe cascade;
                DROP TABLE IF EXISTS ingredient cascade;
                DROP TABLE IF EXISTS comment cascade;
                DROP TABLE IF EXISTS user_menu cascade;
                DROP TABLE IF EXISTS menuContents cascade;
                DROP TABLE IF EXISTS ingredients_of_meal cascade;
                
            ''')
connection.commit()

for statement in TABLE_CREATE_QUERY:
    cursor.execute(statement)


response = requests.get("https://www.themealdb.com/api/json/v1/1/search.php?f=a")
data = response.json()


connection.commit()

#inserting admin's country
cursor.execute('''INSERT INTO country (name) VALUES ('adminLand');''')
connection.commit()

#inserting admin to user table once
cursor.execute('''INSERT INTO "user" (name, country_id) VALUES ('admin', (select id from country where name='adminLand'));''')
connection.commit()

#for every recipe in meals
for j in range(len(data["meals"])):
    #insert its country if it does not exist
    cursor.execute('''INSERT INTO country (name) VALUES ('%s') ON CONFLICT DO NOTHING;''' % (data["meals"][j]["strArea"]))
    connection.commit()

    cursor.execute('''INSERT INTO category (name) VALUES ('%s') ON CONFLICT DO NOTHING;''' % (data["meals"][j]["strCategory"]))
    connection.commit()

    #insert its category if it does not exist
    cursor.execute('''INSERT INTO meal (name, country_id, category_id, photo_url) VALUES (%s, (select id from country where name=%s), (select id from category where name=%s), %s) ON CONFLICT DO NOTHING;''', (data["meals"][j]["strMeal"], data["meals"][j]["strArea"], data["meals"][j]["strCategory"], data["meals"][j]["strMealThumb"]))
    connection.commit()


    #replace single quote with double single quotes (to aviod to errors if the instruction itself has single quotes like don't)
    new_instruction = data["meals"][j]["strInstructions"].replace("'","''")

    #insert its category (assuming all recipes are unique)
    cursor.execute('''INSERT INTO recipe (name, instruction, user_id, meal_id, drink_alternate, video_url) VALUES ('admins %sth meal', '%s', (select u.id from "user" u where u.name='admin'), (select id from meal where name='%s'), '%s', '%s');''' % (j, new_instruction, data["meals"][j]["strMeal"], data["meals"][j]["strDrinkAlternate"], data["meals"][j]["strYoutube"]))
    connection.commit()

    #there are 20 ingredients at max
    for i in range(20):
        #append the number to the strIngredient
        ingredient = "strIngredient" + str(i+1)

        #if the api sends a meaningfull ingredient
        if data["meals"][j][ingredient] != '' and data["meals"][j][ingredient] is not None:
            #add it if it does not already exist
            cursor.execute('''INSERT INTO ingredient (name) VALUES ('%s') ON CONFLICT DO NOTHING;'''% (data["meals"][j][ingredient]))
            connection.commit()

    #there are 20 quantitites at max
    for i in range(20):
        #append the number to the strMeasure
        measure = "strMeasure" + str(i+1)

        #if the api sends a meaningfull quantity
        if data["meals"][j][measure] != '' and data["meals"][j][measure] is not None and data["meals"][j][measure] != ' ':
            #we also need the ingredient name to connect them via foreign key
            ingredient = "strIngredient" + str(i+1)

            #ingredient quantities are not unique because in a recipe, we might use 30g butter for both the meal and the sauce
            #so, recipe, ingredient and quantity combined are not a unique value.
            #if the butter is 30g and 45g, we can distinguish them by their order ??
            cursor.execute('''INSERT INTO ingredients_of_meal (recipe_id, ingredient_id, measurement_quantity) VALUES ((select id from recipe where name='admins %sth meal'), (select id from ingredient where name='%s'), '%s');''' % (j, data["meals"][j][ingredient], data["meals"][j][measure]))
            connection.commit()


cursor.execute('''SELECT * FROM country;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM category;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM "user";''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM meal;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM recipe;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM ingredient;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM ingredients_of_meal;''')
print(cursor.fetchall())