
import json
import requests
import re
import os
import logging
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from statistics_manager import ServerStats
from recipe_manager import RecipeManager
from urllib.parse import urlparse, parse_qs
from user_manager import UserManager
from Init_Recipe_DB import RecipeDbManager 

class ClientHTTPSRequestHandler(BaseHTTPRequestHandler):
    # Create instances of the statistics, recipe, and user managers
    stats = ServerStats()
    recipe_manager = RecipeManager()
    user_manager = UserManager()

    # Configure logging to file
    logging.basicConfig(filename='recipe_server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    # Set common headers for responses
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Handle GET requests
    def do_GET(self):
        user_agent = self.headers.get('User-Agent', 'Unknown')
        self.log_message("GET request, Path: %s\n", str(self.path))
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Increment request count for analytics
        if not re.search(r'\.[a-zA-Z0-9]+$', path):
            self.stats.increment_request_count('GET', self.client_address, user_agent, path, self.user_manager._logged_in)        
        
        # Route the GET request based on the path
        if path == '/':
            self.serve_file('templates/index.html', 'text/html')
        elif path.startswith('/static/'):
            self.serve_static_files(path)
        elif path == '/recipes':
            self.handle_recipes_request(parsed_path.query)
        elif path == '/logout':
            self.handle_logout_request()
        else:
            self.send_error_page(404)

    # Handle POST requests
    def do_POST(self):
        user_agent = self.headers.get('User-Agent', 'Unknown')
        self.log_message("POST request, Path: %s\n", str(self.path))
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if not re.search(r'\.[a-zA-Z0-9]+$', path):
            # exclude static files from the request count statistics
            self.stats.increment_request_count('POST', self.client_address, user_agent, path, self.user_manager._logged_in)

        # Route the POST request based on the path
        if path == '/login':
            self.handle_login(data)
        elif path == '/recipes/add':
            self.add_recipe(data)
        elif path == '/openai':
            self.handle_openai_request(data)            
        elif path.startswith('/recipes/rate/'):
            self.rate_recipe(path, data)
        elif self.path == '/register':
            success, message = self.user_manager.register_user(data['username'], data['password'], data['email'])
            self.send_response(200 if success else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success, 'message': message}).encode())
        else:
            print("path = ", path)
            self.send_error_page(404)
    
    def handle_login(self, data):
        username = data.get('username')
        password = data.get('password')
        # ckeck the input data
        if not all([username, password]):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': False, 'message': 'Missing username or password'}).encode())
            return
        
        # check the credentials
        if self.user_manager.check_credentials(username, password):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Login successful'}).encode())
            # set flag to indicate that the user is logged in
            self.user_manager.set_logged_in(username)
        else:
            # send error message to the user
            self.send_response(401)  # Unauthorized
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': False, 'message': 'Invalid username or password'}).encode())

    # Method to send error pages
    def send_error_page(self, status_code):
        error_file_path = f'templates/{status_code}.html'
        try:
            with open(error_file_path, 'rb') as file:
                self.send_response(status_code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            # If no custom error file, send default error message
            self.send_response(status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>{status_code} Error</h1><p>Page not found.</p></body></html>".encode('utf-8'))

    # serve static files
    def serve_static_files(self, path):
        file_path = path[1:]  # Remove the leading '/'
        file_extension = os.path.splitext(file_path)[1]
        content_type = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }.get(file_extension, 'application/octet-stream')
        self.serve_file(file_path, content_type)

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self._set_headers(200, content_type)
                self.wfile.write(file.read())
        except FileNotFoundError:
            # If the file is not found, send a 404 error
            self.send_error_page(404)

    def handle_logout_request(self):
        print("Logging out user")
        self.user_manager.set_logged_in(False)
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Logout successful'}).encode())
        
    def handle_recipes_request(self, query):
        query_components = parse_qs(query)
        # Get the tag from the query parameters
        tag = query_components.get('tag', [None])[0]
        # Get recipes based on the tag, or all recipes if no tag provided
        recipes = self.recipe_manager.get_all_recipes(tag)
        self._set_headers()
        self.wfile.write(json.dumps(recipes).encode())

    def add_recipe(self, data): 
        # check if user is logged in
        if not self.user_manager._logged_in:
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": False, "message": "User not logged in"}).encode())
            return
        try:
            # check if all required data is provided
            if not all([data.get('name'), data.get('tags'), data.get('ingredients'), data.get('instructions')]):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing or invalid data for the recipe'}).encode())
                return
            # add new recipe
            # **data unpacks the dictionary to pass the key-value pairs as arguments
            self.recipe_manager.add_new_recipe(**data)
            self._set_headers(201)
            self.wfile.write(json.dumps({'message': 'Recipe added successfully'}).encode())
        except Exception as e:
            # if an error occurs, send a 500 error response
            self.send_error_page(500)
            print(e)

    def rate_recipe(self, path, data):
        # check if user is logged in
        if not self.user_manager._logged_in:
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": False, "message": "User not logged in"}).encode())
            return
        try:
            parts = path.split('/')
            if len(parts) >= 4:
                # Parse the recipe ID from the path
                recipe_id = int(parts[3])
                rating = data.get('rating')
                user_id = self.user_manager._user_id
                # Rate the recipe
                if self.recipe_manager.rate_recipe(recipe_id, rating, user_id):
                    # Send a success response
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"success": True}).encode())
                    self.end_headers()
                else:
                    # Send a 404 error in case of a failure
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Recipe not found"}).encode())
            else:
                # Send a 404 error if the path is invalid
                raise ValueError("Invalid path format")
        except ValueError as e:
            self.send_error_page(404)

    def handle_openai_request(self, prompt):
        # check if user is logged in
        if not self.user_manager._logged_in:
            self._set_headers(401)
            self.wfile.write(json.dumps({"error": False, "message": "User not logged in"}).encode())
            return        
        print ("data = ", prompt) #debug
        # Get the OpenAI API key from the environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        url = "https://api.openai.com/v1/chat/completions"
        # Get the top ingredients for the user
        top_ingredients = self.recipe_manager.get_top_ingredients_by_user(self.user_manager._user_id)
        print("top_ingredients = ", top_ingredients)
        if top_ingredients:
            # Add the top ingredients to the prompt
            ingredient_text = ', '.join(top_ingredients)
            enhanced_prompt = f"{prompt} and add only few ingredients from the list without relation to proportions: {ingredient_text}."
        else:
            # Use the original prompt if no top ingredients are available
            enhanced_prompt = prompt

        # create the request headers and data
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Provide short and simple recipes. The resipe should have a name, tags, list ingredients, and instructions. \
                    The response must be in json format with mandatory fields: name, tags, ingredients, instructions and without extra symbols."
                },
                {
                    "role": "user",
                    "content": str(enhanced_prompt)
                }
            ]
        }
        # Make a POST request to the OpenAI API
        response = requests.post(url, headers=headers, json=data)
        print ("responce=", response.content)
        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            print("response_json = ", response_json)
            message_content = response_json['choices'][0]['message']['content']
            print("message_content = ", message_content)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(message_content).encode())
        else:
            # Handle errors
            self.send_response(response.status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Failed to process request with OpenAI"}).encode())

    # log_message method to log the request details
    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" %
                     (self.client_address[0],
                      self.log_date_time_string(),
                      format % args))

def run(server_class=HTTPServer, handler_class=ClientHTTPSRequestHandler, port=8443, start_db=RecipeDbManager):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    # SSL context setup for HTTPS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert/cert.pem', keyfile='cert/key.pem')  

    # Initialize database
    start_db()

    # Wrap the server socket in SSL context
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f'Starting HTTPS server on port {port}')
    try:
        httpd.serve_forever()
    except Exception as e:
        print(f"Server error, An unexpected error occurred: {e}")     
        httpd.server_close()

if __name__ == '__main__':
    run()