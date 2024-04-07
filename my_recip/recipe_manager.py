import sqlite3
import json
from datetime import datetime

class RecipeManager:
    def __init__(self, db_path='recipes.db'):
        self.db_path = db_path

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_recipes(self, tag_filter=None):
        print("Connecting to database...")
        conn = self.get_db_connection()
        c = conn.cursor()
        print("Executing SELECT query...")
        if tag_filter:
            c.execute("SELECT * FROM recipes WHERE tags LIKE ?", ('%' + tag_filter + '%',))
        else:
            c.execute("SELECT * FROM recipes")
        recipes = [dict(row) for row in c.fetchall()]
        conn.close()
        return recipes

    def rate_recipe(self, id, rating):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE recipes SET rating = ? WHERE id = ?", (rating, id))
        changes = c.rowcount
        conn.commit()
        conn.close()
        return changes > 0

    def add_recipe_tag(self, id, tag):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT tags FROM recipes WHERE id = ?", (id,))
        result = c.fetchone()
        if result:
            tags = json.loads(result['tags'])
            if tag not in tags:
                tags.append(tag)
                c.execute("UPDATE recipes SET tags = ? WHERE id = ?", (json.dumps(tags), id))
                conn.commit()
                conn.close()
                return True
    
    def get_recipes_by_rating(self, rating):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM recipes WHERE rating = ?', (rating,))
        recipes_rows = c.fetchall()
        conn.close()

        recipes = []
        for row in recipes_rows:
            recipe = {
                'id': row[0],
                'name': row[1],
                'tags': json.loads(row[2]),
                'ingredients': json.loads(row[3]),
                'instructions': json.loads(row[4]),
                'rating': row[5],
                'date_created': row[6]                
            }
            recipes.append(recipe)
        return recipes
    
    def add_new_recipe(self, name, tags, ingredients, instructions, rating):
        conn = self.get_db_connection()
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c = conn.cursor()
        c.execute('''INSERT INTO recipes (name, tags, ingredients, instructions, rating, date_created) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  (name, json.dumps(tags), json.dumps(ingredients), json.dumps(instructions), rating, date_created,))
        conn.commit()
        conn.close()