import {
    fetchRecipes, 
    showAddRecipeForm, 
    hideAddRecipeForm, 
    submitAddRecipeForm, 
    login, 
    logout, 
    showSignInForm,
    register, 
    hideRegForm, 
    sendToOpenAI,
    validateSearch
} from './module.js';

document.addEventListener('DOMContentLoaded', function() {
    // Grab references to various buttons and input fields from the DOM
    const showFormButton = document.getElementById('showFormButton');
    const addRecipeForm = document.getElementById('addRecipeForm');
    const cancelButton = document.getElementById('cancelButton');
    const searchButton = document.getElementById('searchButton');
    const loginButton = document.getElementById('loginButton');
    const logoutButton = document.getElementById('logoutButton');
    const signinButton = document.getElementById('signinButton');
    const registerButton = document.getElementById('registerButton');
    const cancelRegButton = document.getElementById('cancelRegButton');
    const sendToOpenAIButton = document.getElementById('sendToOpenAIButton');
    const passwordInput = document.getElementById('password');
    const searchInput = document.getElementById('searchArea');
    

    // Initial call to fetch and display all recipes
    fetchRecipes(); // Fetch all recipes when the page loads

    searchInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            validateSearch()
        }
    })

    // Listener for sending a request to OpenAI with selected dietary preferences and cuisine type
    sendToOpenAIButton.addEventListener('click', function() {
        const dietCheckboxes = document.querySelectorAll('input[name="diet"]:checked');
        let diets = Array.from(dietCheckboxes).map(checkbox => checkbox.value).join(', ');
        if (diets === '') {
            diets = 'any diet';
        }
        const cuisine = document.getElementById('cuisineSelect').value;
        const ingredients_from_user = document.getElementById('ingredients_from_user').value;
        let promptText = `Generate a recipe for ${cuisine} cuisine with the following dietary preferences: ${diets} and ingredients: ${ingredients_from_user}.`;
        console.log('promptText:', promptText);
        sendToOpenAI(JSON.stringify({ prompt: promptText }))
    });

    // Add event listener to the password input field to allow the user to press Enter to login
    passwordInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default behavior of the Enter key
            login(); // Execute the login function
        }
    });

    // Add event listeners for various user actions like showing forms, logging in, registering, etc.
    searchButton.addEventListener('click', validateSearch);
    showFormButton.addEventListener('click', showAddRecipeForm);
    cancelButton.addEventListener('click', hideAddRecipeForm);
    addRecipeForm.addEventListener('submit', submitAddRecipeForm);    
    loginButton.addEventListener('click', login);
    logoutButton.addEventListener('click', logout);
    signinButton.addEventListener('click', showSignInForm);
    registerButton.addEventListener('click', register);
    cancelRegButton.addEventListener('click', hideRegForm);
    
});
    