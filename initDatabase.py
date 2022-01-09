import psycopg2
import requests

TABLE_CREATE_QUERY = [
        '''CREATE TABLE IF NOT EXISTS country (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE
        )''',

        '''CREATE TABLE IF NOT EXISTS category (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE
            )''',

        '''CREATE TABLE IF NOT EXISTS meal (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE,
            category_id int NOT NULL,
            photo_url VARCHAR,
            coisine_name VARCHAR(80),
            country_id INTEGER NOT NULL
            )''',
 
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80),
            surname VARCHAR(80),
            mail VARCHAR(80),
            password VARCHAR(80),
            age INTEGER,
            eduHistory INTEGER,
            gender INTEGER,
            country_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL
            )''',
 
        '''CREATE TABLE IF NOT EXISTS recipe (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            meal_id INTEGER NOT NULL,
            name VARCHAR(80) UNIQUE,
            instruction VARCHAR,
            portion VARCHAR(50),
            drink_alternate VARCHAR(50),
            video_url VARCHAR(80)
            )''',
    
        '''CREATE TABLE IF NOT EXISTS ingredient (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            protein FLOAT,
            calorie FLOAT,
            fat FLOAT,
            type VARCHAR(50)
            )''',

        '''CREATE TABLE IF NOT EXISTS comment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            message VARCHAR(200),
            created_date INTEGER,
            updated_date INTEGER,
            text_color VARCHAR(50),
            language VARCHAR(50)
            )''',

        '''CREATE TABLE IF NOT EXISTS ingredients_of_meal (
            id SERIAL PRIMARY KEY,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            measurement_quantity VARCHAR(60)
            )''',

        '''CREATE TABLE IF NOT EXISTS userMenu (
            id SERIAL PRIMARY KEY,
            title VARCHAR(50),
            description VARCHAR,
            created_date INTEGER,
            updated_date INTEGER,
            notes VARCHAR,
            user_id INTEGER NOT NULL
            )''',

        '''CREATE TABLE IF NOT EXISTS menuContent (
            id SERIAL PRIMARY KEY,
            menu_id int NOT NULL,
            meal_id int NOT NULL
            )''',

        '''ALTER TABLE meal ADD FOREIGN KEY (country_id) REFERENCES country (id) ON DELETE SET NULL ON UPDATE CASCADE''',

        '''ALTER TABLE meal ADD FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE SET NULL ON UPDATE CASCADE''',

        '''ALTER TABLE users ADD FOREIGN KEY (country_id) REFERENCES country (id) ON DELETE SET NULL ON UPDATE CASCADE''',

        '''ALTER TABLE recipe ADD FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE recipe ADD FOREIGN KEY (meal_id) REFERENCES meal (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE comment ADD FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE comment ADD FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE ingredients_of_meal ADD FOREIGN KEY (recipe_id) REFERENCES recipe (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE ingredients_of_meal ADD FOREIGN KEY (ingredient_id) REFERENCES ingredient (id) ON DELETE CASCADE ON UPDATE CASCADE''',
        
        '''ALTER TABLE menuContent ADD FOREIGN KEY (menu_id) REFERENCES userMenu (id) ON DELETE CASCADE ON UPDATE CASCADE''',

        '''ALTER TABLE menuContent ADD FOREIGN KEY (meal_id) REFERENCES meal (id) ON DELETE SET NULL ON UPDATE CASCADE''',
        
        '''ALTER TABLE userMenu ADD FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE'''


]

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16", sslmode = 'require')
cursor = connection.cursor()

def area2country(argument):
    switcher = {
        "Albanian": "Albania",
        "Moroccan": "Morocco",
        "French": "France",
        "Unknown": "Unknown",
        "Biritsh": "UK",
        "Indian": "India",
        "Italian": "Italy",
        "American": "US",
        "Mexican": "Mexico",
        "Japanese": "Japan",
        "Jamaican": "Jamaica",
        "Chinese": "China",
        "Tunisian": "Tunisia",
        "Turkish": "Turkey",
        "Irish": "Ireland",
        "Greek": "Greece",
        "Croatian": "Croatia",
        "Dutch": "Netherlands",
        "German": "Germany"
    }

    return switcher.get(argument, "Unknown")

#deleting all the previous tables to recreate them
cursor.execute('''
                DROP TABLE IF EXISTS country cascade;
                DROP TABLE IF EXISTS category cascade;
                DROP TABLE IF EXISTS meal cascade;
                DROP TABLE IF EXISTS users cascade;
                DROP TABLE IF EXISTS recipe cascade;
                DROP TABLE IF EXISTS ingredient cascade;
                DROP TABLE IF EXISTS comment cascade;
                DROP TABLE IF EXISTS userMenu cascade;
                DROP TABLE IF EXISTS menuContent cascade;
                DROP TABLE IF EXISTS ingredients_of_meal cascade;
                
            ''')
connection.commit()

for statement in TABLE_CREATE_QUERY:
    cursor.execute(statement)


connection.commit()

#inserting admin's country
cursor.execute('''INSERT INTO country (name) VALUES ('Turkey');''')
connection.commit()

#inserting admin to user table once
cursor.execute('''INSERT INTO users (name, country_id, role_id, password) VALUES ('admin', (select id from country where name='Turkey'), 1, 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3');''')
connection.commit()

z = 0
for c in "abc":
    response = requests.get("https://www.themealdb.com/api/json/v1/1/search.php?f=%s" % (c))
    data = response.json()

    #for every recipe in meals
    for j in range(len(data["meals"])):
        print(z)
        #insert its country if it does not exist
        cursor.execute('''INSERT INTO country (name) VALUES ('%s') ON CONFLICT DO NOTHING;''' % (area2country(data["meals"][j]["strArea"])))
        

        cursor.execute('''INSERT INTO category (name) VALUES ('%s') ON CONFLICT DO NOTHING;''' % (data["meals"][j]["strCategory"]))
        

        #insert its category if it does not exist
        cursor.execute('''INSERT INTO meal (name, country_id, category_id, photo_url, coisine_name) VALUES (%s, (select id from country where name=%s), (select id from category where name=%s), %s, %s) ON CONFLICT DO NOTHING;''', (data["meals"][j]["strMeal"], area2country(data["meals"][j]["strArea"]), data["meals"][j]["strCategory"], data["meals"][j]["strMealThumb"], data["meals"][j]["strArea"]))


        #replace single quote with double single quotes (to aviod to errors if the instruction itself has single quotes like don't)
        new_instruction = data["meals"][j]["strInstructions"].replace("'","''")

        #insert its category (assuming all recipes are unique)
        cursor.execute('''INSERT INTO recipe (name, instruction, user_id, meal_id, drink_alternate, video_url, portion) VALUES ('System''s %s recipe', '%s', (select u.id from users u where u.name='admin'), (select id from meal where name='%s'), '%s', '%s', '%s');''' % (z, new_instruction, data["meals"][j]["strMeal"], data["meals"][j]["strDrinkAlternate"], data["meals"][j]["strYoutube"], 0))
        z = z + 1
        

        #there are 20 ingredients at max
        for i in range(20):
            #append the number to the strIngredient
            ingredient = "strIngredient" + str(i+1)

            #if the api sends a meaningfull ingredient
            if data["meals"][j][ingredient] != '' and data["meals"][j][ingredient] is not None:
                #add it if it does not already exist
                cursor.execute('''INSERT INTO ingredient (name, protein, calorie, fat) VALUES ('%s', '%s', '%s', '%s') ON CONFLICT DO NOTHING;'''% (data["meals"][j][ingredient], 0, 0, 0))
                

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
                cursor.execute('''INSERT INTO ingredients_of_meal (recipe_id, ingredient_id, measurement_quantity) VALUES ((select id from recipe where name='System''s %s recipe'), (select id from ingredient where name='%s'), '%s');''' % (j, data["meals"][j][ingredient], data["meals"][j][measure]))
                
        
        connection.commit()


cursor.execute('''SELECT * FROM country;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM category;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM users;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM meal;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM recipe;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM ingredient;''')
print(cursor.fetchall())

cursor.execute('''SELECT * FROM ingredients_of_meal;''')
print(cursor.fetchall())
