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
        # Modified SQL query to join recipes with recipe_ratings and calculate average rating
        if tag_filter:
            c.execute("""
                SELECT recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created, AVG(recipe_ratings.rating) AS average_rating
                FROM recipes
                LEFT JOIN recipe_ratings ON recipes.id = recipe_ratings.recipe_id
                WHERE recipes.tags LIKE ?
                GROUP BY recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created
                """, ('%' + tag_filter + '%',))
        else:
            c.execute("""
                SELECT recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created, AVG(recipe_ratings.rating) AS average_rating
                FROM recipes
                LEFT JOIN recipe_ratings ON recipes.id = recipe_ratings.recipe_id
                GROUP BY recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created
                """)
        # Fetch all rows and convert them to dictionaries to include the new average_rating field
        recipes = [dict(row) for row in c.fetchall()]
        print("Recipes fetched:", recipes)
        conn.close()
        return recipes

    def rate_recipe(self, recipe_id, rating, user_id):
        conn = self.get_db_connection()
        c = conn.cursor()
        # Current timestamp for the rating event
        rated_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Insert a new rating into the recipe_ratings table
        c.execute('''
            INSERT INTO recipe_ratings (recipe_id, user_id, rating, rated_on)
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, user_id, rating, rated_on))
        conn.commit()
        row_id = c.lastrowid  # Get the last inserted id
        conn.close()
        return row_id

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
    
    def add_new_recipe(self, name, tags, ingredients, instructions, rating=None):
        conn = self.get_db_connection()
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c = conn.cursor()
        
        # Insert the new recipe into the recipes table
        c.execute('''INSERT INTO recipes (name, tags, ingredients, instructions, date_created) 
                    VALUES (?, ?, ?, ?, ?)''', 
                (name, json.dumps(tags), json.dumps(ingredients), json.dumps(instructions), date_created))
        recipe_id = c.lastrowid  # Get the id of the newly inserted recipe

        # Set default rating if none provided
        default_rating = 4 if rating is None else rating

        # Insert the default or provided rating into the recipe_ratings table
        rated_on = datetime.now().isoformat()  # Use a consistent datetime format for the rating timestamp
        c.execute('''INSERT INTO recipe_ratings (recipe_id, rating, rated_on) 
                    VALUES (?, ?, ?)''', 
                (recipe_id, default_rating, rated_on))
        
        conn.commit()
        conn.close()

        return recipe_id