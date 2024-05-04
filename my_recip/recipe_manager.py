import sqlite3
import json
from datetime import datetime
from collections import Counter
from Init_Recipe_DB import RecipeDbManager

# Class to manage recipes
class RecipeManager:
    def __init__(self):
        # Get the database path from RecipeDbManager
        self.db_path = RecipeDbManager().db_path
    
    # Method to get a database connection
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Method to get all recipes from the database
    def get_all_recipes(self, tag_filter=None):
        print("Connecting to database...")
        conn = self.get_db_connection()
        c = conn.cursor()
        print("Executing SELECT query...")
        # Fetch recipes 
        if tag_filter:
            # Filter recipes by tag
            c.execute("""
                SELECT recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created, AVG(recipe_ratings.rating) AS average_rating
                FROM recipes
                LEFT JOIN recipe_ratings ON recipes.id = recipe_ratings.recipe_id
                WHERE recipes.tags LIKE ?
                GROUP BY recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created
                """, ('%' + tag_filter + '%',))
        else:
            # Fetch all recipes
            c.execute("""
                SELECT recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created, AVG(recipe_ratings.rating) AS average_rating
                FROM recipes
                LEFT JOIN recipe_ratings ON recipes.id = recipe_ratings.recipe_id
                GROUP BY recipes.id, recipes.name, recipes.tags, recipes.ingredients, recipes.instructions, recipes.date_created
                """)
        # Convert the result to a list of dictionaries
        recipes = [dict(row) for row in c.fetchall()]
        # sort the recipes by creation date
        recipes.sort(key=lambda x: x['date_created'], reverse=True)
        print("Recipes fetched:", recipes)
        conn.close()
        return recipes

    # Method to rate a recipe
    def rate_recipe(self, recipe_id, rating, user_id):
        # Connect to the database
        conn = self.get_db_connection()
        c = conn.cursor()
        # Current timestamp for the rating event
        rated_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if the user has already rated this recipe
        c.execute('''
            SELECT id FROM recipe_ratings WHERE recipe_id = ? AND user_id = ?
        ''', (recipe_id, user_id))
        existing_rating = c.fetchone()

        # Insert or update the rating
        if existing_rating:
            # Update the existing rating
            c.execute('''
                UPDATE recipe_ratings SET rating = ?, rated_on = ? WHERE id = ?
            ''', (rating, rated_on, existing_rating[0]))
            affected_row_id = existing_rating[0] 
        else:
            # Insert a new rating if not existing
            c.execute('''
                INSERT INTO recipe_ratings (recipe_id, user_id, rating, rated_on)
                VALUES (?, ?, ?, ?)
            ''', (recipe_id, user_id, rating, rated_on))
            affected_row_id = c.lastrowid
        conn.commit()
        conn.close()
        print("row_id:", affected_row_id)
        # Return the affected row id
        return affected_row_id
   
    # Method to add a new recipe
    def add_new_recipe(self, name, tags, ingredients, instructions, rating=None):
        # Connect to the database
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

    # Method to get top ingredients by user
    def get_top_ingredients_by_user(self, user_id):
        # Connect to the database
        conn = self.get_db_connection()
        c = conn.cursor()
        # Get all ingredients for recipes rated by the user with a rating greater than 4
        c.execute('''
            SELECT r.ingredients
            FROM recipes r
            JOIN recipe_ratings rr ON r.id = rr.recipe_id
            WHERE rr.user_id = ? AND rr.rating > 4
        ''', (user_id,))
        all_ingredients = []
        for row in c.fetchall():
            ingredients_list = json.loads(row['ingredients'])
            all_ingredients.extend(ingredients_list)
        conn.close()

        # Count and find the top 10 most common ingredients
        ingredient_count = Counter(all_ingredients)
        print("ingredient_count:", ingredient_count)
        # Get the top 10 ingredients
        top_ingredients = [ingredient for ingredient, count in ingredient_count.most_common(10)]
        return top_ingredients    