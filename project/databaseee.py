import psycopg2

connection = psycopg2.connect("postgres://pylafsgesfibkp:008aa6f8817e256b98e034493c344833da4b0447a1d11fb05073ea4ec87447ff@ec2-35-153-88-219.compute-1.amazonaws.com:5432/db0rfao3q1lr16", sslmode = 'require')
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
                DROP TABLE IF EXISTS userMenu cascade;
                DROP TABLE IF EXISTS menuContent cascade;
                DROP TABLE IF EXISTS ingredients_of_meal cascade;
                
            ''')
connection.commit()
connection.commit()
print(cursor.fetchall())
