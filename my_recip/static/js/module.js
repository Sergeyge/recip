var generatedRecipes ="";

export function fetchRecipes(tag = '') {
    // Construct the URL based on whether a tag is provided
    const url = tag ? `/recipes?tag=${encodeURIComponent(tag)}` : '/recipes';
    // Fetch recipes from the server
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
                return `<button class="star" data-rating="${index + 1}" aria-label="Rate as ${index + 1}">${recipe.average_rating > index ? '★' : '☆'}</button>`;
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
    document.getElementById('addRecipeForm').style.display = 'block';
}

export function hideAddRecipeForm() {
    console.log("Cancel button clicked");
    // Hide the form
    addRecipeForm.style.display = 'none'; 
}

export function submitAddRecipeForm(event) {
    // Prevent the default form submission
    event.preventDefault(); 
    // Get the form data
    const formData = {
        name: event.target.name.value,
        // Split comma-separated tags and trim whitespace
        tags: event.target.tags.value.split(',').map(tag => tag.trim()), 
        ingredients: event.target.ingredients.value.split(',').map(ingredient => ingredient.trim()),
        instructions: event.target.instructions.value.split(',').map(instruction => instruction.trim()),
        rating: 4, // Default rating
    };
    // Send the form data to the server
    fetch('/recipes/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    // Parse the JSON response
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Log success message
        addRecipeForm.style.display = 'none'; // Hide the form
        showFormButton.style.display = 'block'; // Show the "Add New Recipe" button again
        fetchRecipes(); // Reload recipes

    })
    // Log any errors
    .catch(error => console.error('Error adding recipe:', error));
}

export function saveGeneratedResipe() {
    // Prevent the default form submission
    fetch('/recipes/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(generatedRecipes),
    })
    // Parse the JSON response
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Log success message
        fetchRecipes(); // Reload recipes
        document.getElementById('saveGeneratedRecipeButton').style.display = 'none';
        document.getElementById('openAIResponse').style.display = 'none';
    })
    // Log any errors
    .catch(error => console.error('Error adding recipe:', error));
}

export function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    // validate username and password
    if (!username || !password) {
        alert('Please enter a username and password.');
        return;
    }
    // Send the login request to the server
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    })
    // Parse the JSON response
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide the login form and display the user greeting and OpenAI request form, display the username
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('usernameDisplay').textContent = username;
            document.getElementById('userGreeting').style.display = 'block';
            document.getElementById('openAIRequest').style.display = 'block';

        } else {
            // Display an error message if login fails
            alert('Login failed: ' + data.message);
        }
    })
    // Log any errors
    .catch(error => console.error('Error logging in:', error));
}

export function logout() {
    // Send a logout request to the server
    fetch('/logout', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    // Parse the JSON response
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Logout successful') {
            alert('Logout successful');
            // Hide the user greeting, addRecipeForm and OpenAI request form, display the login form
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('userGreeting').style.display = 'none';
            document.getElementById('openAIRequest').style.display = 'none';
            document.getElementById('addRecipeForm').style.display = 'none';

        } else {
            // Display an error message if logout fails
            alert('Logout failed: ' + data.message);
        }
    })
    .catch(error => console.error('Error logging out:', error));
}

export function sendToOpenAI(question) {
    console.log("Send to OpenAI button clicked");
    // Send request to the server with prompt to OpenAI
    fetch('/openai', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: question
    })
    // Parse the JSON response
    .then(response => response.json())
    .then(data => {
        console.log('OpenAI response:', JSON.parse(data));
        generatedRecipes=JSON.parse(data)
        console.log('Name', generatedRecipes.name);
        const responseElement = document.getElementById('openAIResponse');
        let htmlContent = `<h2>${generatedRecipes.name}</h2>`;
        htmlContent += `<p><strong>Tags:</strong> ${generatedRecipes.tags.join(', ')}</p>`;
        htmlContent += `<h3>Ingredients:</h3><ul>`;
        generatedRecipes.ingredients.forEach(ingredient => {
            htmlContent += `<li>${ingredient}</li>`;
        });
        htmlContent += `</ul><h3>Instructions:</h3><ol>`;
        generatedRecipes.instructions.forEach(instruction => {
            htmlContent += `<li>${instruction}</li>`;
        });
        htmlContent += `</ol>`;
        responseElement.innerHTML = htmlContent; // Display the formatted recipe
        document.getElementById('openAIResponse').style.display = 'block';
        document.getElementById('saveGeneratedRecipeButton').style.display = 'block';
    })
    .catch(error => {
        console.error('Error sending prompt to OpenAI:', error);
        document.getElementById('openAIResponse').textContent = 'Failed to get response from OpenAI.';
    });
}



export function showSignInForm() {  
    // Hide the login and search forms, display the register form
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('searchArea').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

export function register() {
    // Get the username, password, and email from the form
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const email = document.getElementById('regEmail').value;
    // validate username and password
    if (!validatePassword()) {
        alert('Please ensure the password meets all requirements.');
        return false;
    }

    if (!validateEmail(email)) {
        alert("Please enter a valid email address.");
        return false;
    }
    // Send the registration request to the server
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, email})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display a success message and hide the register form
            alert('Registration successful');
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('searchArea').style.display = 'block';
            document.getElementById('loginForm').style.display = 'block';
        } else {
            alert('Registration failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error registering:', error);
        alert('Error registering: ' + error.message);
        
    });
}

export function hideRegForm() { 
    // Hide the register form and display the login form
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('searchArea').style.display = 'block';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('passwordError').style.display = 'none';
    document.getElementById('emailError').style.display = 'none';
}

export function validateSearch() {
    const tag = searchTagInput.value.trim();
    // check if the tag is empty
    if (tag === '') {
        document.getElementById('searchTagInput').placeholder = 'Add a tag to search';
    }
    else {
        document.getElementById('searchTagInput').value = ''; // Clear the search input field
        document.getElementById('searchTagInput').placeholder = 'Search by tag...';
    }
    fetchRecipes(tag); // Fetch recipes with the specified tag or all recipes if the tag is empty
}


function validatePassword() {
    // Validate the password using a regular expression
    const password = document.getElementById('regPassword').value;
    const regex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$/;
    const errorMessage = document.getElementById('passwordError');

    if (regex.test(password)) {
        errorMessage.style.display = 'none';
        return true;
    } else {
        errorMessage.style.display = 'block';
        return false;
    }
}

function validateEmail(email) {
    // Validate the email using a regular expression
    const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    const errorMessage = document.getElementById('emailError');
    
    if (regex.test(email)) {
        errorMessage.style.display = 'none';
        return true;
    } else {
        errorMessage.style.display = 'block';
        return false;
    }    
}
