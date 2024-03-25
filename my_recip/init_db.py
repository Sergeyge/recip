import sqlite3
import json
from datetime import datetime

def create_table():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            tags TEXT,
            ingredients TEXT,
            instructions TEXT,
            rating INTEGER DEFAULT 0,
            date_created TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_initial_data():
    current_date_iso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    recipes = [
        # Your recipe data here
    ]

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    for recipe in recipes:
        c.execute('INSERT INTO recipes (name, tags, ingredients, instructions, rating) VALUES (?, ?, ?, ?, ?)',
                  (recipe["name"], json.dumps(recipe["tags"]), json.dumps(recipe["ingredients"]), json.dumps(recipe["instructions"]), recipe["rating"], ))
    conn.commit()
    conn.close()

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

if __name__ == '__main__':
    create_table()
    insert_initial_data()
    print_all_recipes()
    print("Database initialized and populated with initial data.")
