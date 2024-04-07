from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from recipe_manager import RecipeManager

app = Flask(__name__)
CORS(app)
recipe_manager = RecipeManager()

@app.route('/')
def index():
    """Serve the index HTML page."""
    return render_template('index.html')

@app.route('/recipes', methods=['GET'])
def get_recipes():
    # print("Fetching all recipes...")
    # """Endpoint to retrieve recipes. Optionally filter by tag."""
    # tag = request.args.get('tag', None)
    # recipes = recipe_manager.get_all_recipes(tag_filter=tag)
    # return jsonify([recipe for recipe in recipes])
    tag = request.args.get('tag')
    if tag:
        recipes = recipe_manager.get_all_recipes(tag)
    else:
        recipes = recipe_manager.get_all_recipes()
    return jsonify(recipes)


@app.route('/recipes/rating/<int:rating>', methods=['GET'])
def get_recipes_by_rating(rating):
    recipes = recipe_manager.get_recipes_by_rating(rating)
    if recipes:
        return jsonify(recipes)
    else:
        return jsonify({"message": "No recipes found with the specified rating"}), 404


@app.route('/recipes/rate/<int:recipe_id>', methods=['POST'])
def rate_recipe(recipe_id):
    """Endpoint to rate a recipe."""
    data = request.get_json()
    rating = data.get('rating')
    if recipe_manager.rate_recipe(recipe_id, rating):
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Recipe not found"}), 404

@app.route('/recipes/add_tag/<int:recipe_id>', methods=['POST'])
def add_tag(recipe_id):
    """Endpoint to add a tag to a recipe."""
    data = request.get_json()
    tag = data.get('tag')
    if recipe_manager.add_recipe_tag(recipe_id, tag):
        return jsonify({"success": True})
    else:
        print("Recipe not found")
        return jsonify({"error": "Recipe not found"}), 404

@app.route('/recipes/add', methods=['POST'])
def add_recipe():
    # Extract data from the request
    data = request.get_json()
    name = data.get('name')
    tags = data.get('tags')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    rating = data.get('rating')
    # date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Validate data (basic validation)
    if not all([name, tags, ingredients, instructions, isinstance(rating, int)]):
        return jsonify({'error': 'Missing or invalid data for the recipe'}), 400

    # Add the new recipe
    try:
        recipe_manager.add_new_recipe(name, tags, ingredients, instructions, rating)
        return jsonify({'message': 'Recipe added successfully'}), 201
    except Exception as e:
        # Handle errors (e.g., database errors) and return a server error message
        print(e)  # Log the error for debugging
        return jsonify({'error': 'Could not add the recipe'}), 500


if __name__ == '__main__':
    app.run(debug=True)
