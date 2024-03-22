document.addEventListener('DOMContentLoaded', function() {
    fetch('/recipes')
    .then(response => response.json())
    .then(data => {
        const recipesElement = document.getElementById('recipes');
        data.forEach(recipe => {
            // Ensure tags are an array
            let tags = recipe.tags;
            if (typeof tags === 'string') {
                try {
                    tags = JSON.parse(tags);
                } catch(e) {
                    console.error('Error parsing tags for recipe:', recipe.name, e);
                    tags = [];
                }
            }

            // Ensure ingredients are an array
            let ingredients = recipe.ingredients;
            if (typeof ingredients === 'string') {
                try {
                    ingredients = JSON.parse(ingredients);
                } catch(e) {
                    console.error('Error parsing ingredients for recipe:', recipe.name, e);
                    ingredients = [];
                }
            }

            // Ensure instructions are an array
            let instructions = recipe.instructions;
            if (typeof instructions === 'string') {
                try {
                    instructions = JSON.parse(instructions);
                } catch(e) {
                    console.error('Error parsing instructions for recipe:', recipe.name, e);
                    instructions = [];
                }
            }

            const recipeElement = document.createElement('div');
            recipeElement.innerHTML = `
                <h2>${recipe.name}</h2>
                <p><strong>Tags:</strong> ${tags.join(', ')}</p>
                <p><strong>Ingredients:</strong> ${ingredients.join('<br>')}</p>
                <p><strong>Instructions:</strong> ${instructions.join('<br>')}</p>
                <div>Rating: ${recipe.rating}</div>
            `;
            recipesElement.appendChild(recipeElement);
        });
    })
    .catch(error => console.error('Error loading recipes:', error));
});
