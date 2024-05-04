import sqlite3
import json
import hashlib


class RecipeDbManager:
    def __init__(self, db_path='recipes.db'):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        # Establish connection to the SQLite database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create the first table for recipes
        c.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                tags TEXT,
                ingredients TEXT,
                instructions TEXT,
                date_created TEXT
            );
        ''')
        
        # Create the second table for recipe ratings
        c.execute('''
            CREATE TABLE IF NOT EXISTS recipe_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                user_id INTEGER,
                rating INTEGER,
                rated_on TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(recipe_id, user_id)
            );
        ''')
        

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer'            )
        ''')

        c.execute('SELECT * FROM users WHERE username=?', ('admin',))
        if c.fetchone() is None:
                # Insert default admin user
                hashed_password = hashlib.sha256("admin".encode()).hexdigest()
                c.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', ('admin', hashed_password, 'admin@recip.com', 'admin'))


        # Commit the changes and close the connection to the database
        conn.commit()
        conn.close()
        print("Database initialized.")


    def print_all_recipes():
        conn = sqlite3.connect('recipes.db')
        c = conn.cursor()
        c.execute('SELECT * FROM recipes')
        all_recipes = c.fetchall()
        
        for recipe in all_recipes:
            print("Recipe ID:", recipe[0])
            print("Name:", recipe[1])
            print("Tags:", json.loads(recipe[2]))
            print("Ingredients:", json.loads(recipe[3]))
            print("Instructions:", json.loads(recipe[4]))
            print("Rating:", recipe[5])
            print("Date created:", recipe[6])
            print("----------")
