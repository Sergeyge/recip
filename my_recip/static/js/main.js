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
    sendToOpenAI
} from './module.js';

document.addEventListener('DOMContentLoaded', function() {
    // Grab references to various buttons and input fields from the DOM
    const showFormButton = document.getElementById('showFormButton');
    const addRecipeForm = document.getElementById('addRecipeForm');
    const cancelButton = document.getElementById('cancelButton');
    const searchButton = document.getElementById('searchButton');
    const searchTagInput = document.getElementById('searchTagInput');    
    const loginButton = document.getElementById('loginButton');
    const logoutButton = document.getElementById('logoutButton');
    const signinButton = document.getElementById('signinButton');
    const registerButton = document.getElementById('registerButton');
    const cancelRegButton = document.getElementById('cancelRegButton');
    const sendToOpenAIButton = document.getElementById('sendToOpenAIButton');
    

    // Initial call to fetch and display all recipes
    fetchRecipes(); // Fetch all recipes when the page loads
   
    // Add event listener to the search button to fetch recipes based on a tag
    searchButton.addEventListener('click', function() {
        const tag = searchTagInput.value.trim();
        // check if the tag is empty
        if (tag === '') {
            alert('Please enter a tag to search for recipes.');
            return;
        }
        fetchRecipes(tag); // Fetch recipes with the specified tag or all recipes if the tag is empty
    });

    // Listener for sending a request to OpenAI with selected dietary preferences and cuisine type
    sendToOpenAIButton.addEventListener('click', function() {
        const dietCheckboxes = document.querySelectorAll('input[name="diet"]:checked');
        let diets = Array.from(dietCheckboxes).map(checkbox => checkbox.value).join(', ');
        if (diets === '') {
            diets = 'any diet';
        }
        const cuisine = document.getElementById('cuisineSelect').value;
        let promptText = `Generate a recipe for ${cuisine} cuisine with the following dietary preferences: ${diets}.`;
        console.log('promptText:', promptText);
        sendToOpenAI(JSON.stringify({ prompt: promptText }))
    });

    // Add event listeners for various user actions like showing forms, logging in, registering, etc.
    showFormButton.addEventListener('click', showAddRecipeForm);
    cancelButton.addEventListener('click', hideAddRecipeForm);
    addRecipeForm.addEventListener('submit', submitAddRecipeForm);    
    loginButton.addEventListener('click', login);
    logoutButton.addEventListener('click', logout);
    signinButton.addEventListener('click', showSignInForm);
    registerButton.addEventListener('click', register);
    cancelRegButton.addEventListener('click', hideRegForm);
});
    