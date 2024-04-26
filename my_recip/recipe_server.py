from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from statistics_manager import ServerStats
from recipe_manager import RecipeManager
import os
import logging

from user_manager import UserManager

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    stats = ServerStats()
    recipe_manager = RecipeManager()
    user_manager = UserManager()

    logging.basicConfig(filename='recipe_server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        user_agent = self.headers.get('User-Agent', 'Unknown')
        self.stats.increment_request_count('GET', self.client_address, user_agent)

        self.log_message("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        parsed_path = urlparse(self.path)
        path = parsed_path.path
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
        # super().do_GET()

    def do_POST(self):
        user_agent = self.headers.get('User-Agent', 'Unknown')
        self.stats.increment_request_count('POST', self.client_address, user_agent)
        self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/login':
            self.handle_login(data)
        elif path == '/recipes/add':
            self.add_recipe(data)
        elif path.startswith('/recipes/rate/'):
            self.rate_recipe(path, data)
        else:
            self.send_error_page(404)

    def handle_login(self, data):
        username = data.get('username')
        password = data.get('password')
        if self.user_manager.check_credentials(username, password):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Login successful'}).encode())
            # set flag to indicate that the user is logged in
            self.user_manager.set_logged_in(username)
        else:
            self.send_response(401)  # Unauthorized
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Invalid username or password'}).encode())

        
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
            self.send_error_page(404)

    def handle_logout_request(self):
        print("Logging out user")
        self.user_manager.set_logged_in(False)
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Logout successful'}).encode())
        
    def handle_recipes_request(self, query):
        query_components = parse_qs(query)
        tag = query_components.get('tag', [None])[0]
        recipes = self.recipe_manager.get_all_recipes(tag)
        self._set_headers()
        self.wfile.write(json.dumps(recipes).encode())

    def add_recipe(self, data):
        try:
            if not all([data.get('name'), data.get('tags'), data.get('ingredients'), data.get('instructions'), isinstance(data.get('rating'), int)]):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing or invalid data for the recipe'}).encode())
                return
            self.recipe_manager.add_new_recipe(**data)
            self._set_headers(201)
            self.wfile.write(json.dumps({'message': 'Recipe added successfully'}).encode())
        except Exception as e:
            self.send_error_page(500)
            print(e)

    def rate_recipe(self, path, data):
        # check if user is logged in
        if not self.user_manager._logged_in:
            # popup message to user 
            self._set_headers(401)
            self.wfile.write(json.dumps({"success": False, "message": "User not logged in"}).encode())
            return
        try:
            parts = path.split('/')
            if len(parts) >= 4:
                recipe_id = int(parts[3])
                print("Recipe ID parsed:", recipe_id)  # Debugging statement
                rating = data.get('rating')
                if self.recipe_manager.rate_recipe(recipe_id, rating):
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"success": True}).encode())
                    self.end_headers()
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Recipe not found"}).encode())
            else:
                raise ValueError("Invalid path format")
        except ValueError as e:
            self.send_error_page(404)

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s" %
                     (self.client_address[0],
                      self.log_date_time_string(),
                      format % args))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        handler_class.stats.report()  # Report statistics upon shutdown
        httpd.server_close()
if __name__ == '__main__':
    run()