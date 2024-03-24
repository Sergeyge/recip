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
            const ratingStars = Array.from({ length: 5 }, (_, index) => {
                const starValue = index + 1;
                return `<button class="star" data-rating="${starValue}" aria-label="Rate as ${starValue}">${recipe.rating > index ? '★' : '☆'}</button>`;
            }).join('');

            recipeElement.innerHTML = `
                <h2>${recipe.name}</h2>
                <table>
                    <tr>
                        <th>Tags</th>
                        <td>${tags.join(', ')}</td>
                    </tr>
                    <tr>
                        <th>Ingredients</th>
                        <td>${ingredients.join('<br>')}</td>
                    </tr>
                    <tr>
                        <th>Instructions</th>
                        <td>${instructions.join('<br>')}</td>
                    </tr>
                    <tr>
                        <th>Rating</th>
                        <td>${ratingStars}</td>
                    </tr> 
                </table>
            `;
        // After appending recipeElement to the document
        recipeElement.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', function() {
                const newRating = this.getAttribute('data-rating');
                updateRecipeRating(recipe.id, newRating);
            });
        });            
        recipesElement.appendChild(recipeElement);
        });
    })
    .catch(error => console.error('Error loading recipes:', error));

    function updateRecipeRating(recipeId, newRating) {
        fetch(`/recipes/rate/${recipeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rating: newRating }),
        })
        .then(response => {
            if (response.ok) {
                console.log("Rating updated successfully.");
                // Optionally, reload recipes or update the UI accordingly
            } else {
                console.error("Failed to update rating.");
            }
        });
    }    
});
