export function fetchRecipes(tag = '') {
    // Construct the URL based on whether a tag is provided
    const url = tag ? `/recipes?tag=${encodeURIComponent(tag)}` : '/recipes';

    fetch(url)
    .then(response => response.json())
    .then(data => {
        const recipesElement = document.getElementById('recipes');
        recipesElement.innerHTML = ''; // Clear existing recipes before displaying new ones
        if (data.length === 0) {
            // Display a "not found" message if no recipes were found
            recipesElement.innerHTML = '<p>No recipes found.</p>';
            return; // Exit the function early
        }
        data.forEach(recipe => {
            // Check and parse the tags, ingredients, and instructions
            let tags = typeof recipe.tags === 'string' ? JSON.parse(recipe.tags) : recipe.tags;
            let ingredients = typeof recipe.ingredients === 'string' ? JSON.parse(recipe.ingredients) : recipe.ingredients;
            let instructions = typeof recipe.instructions === 'string' ? JSON.parse(recipe.instructions) : recipe.instructions;

            const recipeElement = document.createElement('div');
            const ratingStars = Array.from({ length: 5 }, (_, index) => {
                return `<button class="star" data-rating="${index + 1}" aria-label="Rate as ${index + 1}">${recipe.rating > index ? '★' : '☆'}</button>`;
            }).join('');

            // Constructing and setting innerHTML for recipeElement
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
                        <th>Date Added</th>
                        <td>${recipe.date_created}</td>
                    </tr>                    
                    <tr>
                        <th>Rating</th>
                        <td>${ratingStars}</td>
                    </tr> 
                </table>
            `;

            // Append the new recipeElement to the recipes container
            recipesElement.appendChild(recipeElement);

            // Add event listeners to the rating stars
            recipeElement.querySelectorAll('.star').forEach(star => {
                star.addEventListener('click', function() {
                    const newRating = this.getAttribute('data-rating');
                    updateRecipeRating(recipe.id, newRating);
                });
            });            
        });
    })
    .catch(error => console.error('Error loading recipes:', error));
}

export function updateRecipeRating(recipeId, newRating) {
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
        } else if (response.status === 401) {
            console.error("Failed to update rating: User is not authenticated.");
            alert("Failed to update rating: User is not authenticated.");
        } else {
            console.error("Failed to update rating.");
            alert("Failed to update rating.");
        }
    });
}    

export function showAddRecipeForm() {
    console.log("Show form button clicked");
    addRecipeForm.style.display = 'block'; // Show the form
    showFormButton.style.display = 'none'; // Optionally hide the button
}

export function hideAddRecipeForm() {
    console.log("Cancel button clicked");
    addRecipeForm.style.display = 'none'; // Hide the form
    showFormButton.style.display = 'block'; // Show the "Add New Recipe" button again
}

export function submitAddRecipeForm(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = {
        name: event.target.name.value,
        tags: event.target.tags.value.split(',').map(tag => tag.trim()), // Split comma-separated tags and trim whitespace
        ingredients: event.target.ingredients.value.split(',').map(ingredient => ingredient.trim()),
        instructions: event.target.instructions.value.split(',').map(instruction => instruction.trim()),
        rating: 5, // Default rating
    };
    fetch('/recipes/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Log success message
        addRecipeForm.style.display = 'none'; // Hide the form
        showFormButton.style.display = 'block'; // Show the "Add New Recipe" button again
        fetchRecipes(); // Reload recipes

    })
    .catch(error => console.error('Error adding recipe:', error));
}


export function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('usernameDisplay').textContent = username;
            document.getElementById('userGreeting').style.display = 'block';

        } else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch(error => console.error('Error logging in:', error));
}

export function logout() {
    console.log("Logout button clicked");
    fetch('/logout', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Logout successful') {
            alert('Logout successful');
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('userGreeting').style.display = 'none';

        } else {
            alert('Logout failed: ' + data.message);
        }
    })
    .catch(error => console.error('Error logging out:', error));
}

