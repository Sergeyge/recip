from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import ssl
from urllib.parse import urlparse
from statistics_manager import ServerStats

class StatisticsRequestHandler(BaseHTTPRequestHandler):
    # Initialize a statistics manager instance for tracking server stats.
    stats_manager = ServerStats()

    def do_GET(self):
        # Parse the path from the incoming GET request
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve the statistics index page
        if path == '/':
            self.serve_file('statistics/index.html', 'text/html')
        # Serve static files under the /statistics/ directory
        elif path.startswith('/statistics/'):
            self.serve_static_files(path)
        # Provide the API for accessing statistics data
        elif self.path == '/api/statistics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = self.stats_manager.report()
            self.wfile.write(json.dumps(stats).encode())

    def serve_file(self, file_path, content_type):
        # Try to open and serve the file requested
        try:
            with open(file_path, 'rb') as file:
                self._set_headers(200, content_type)
                self.wfile.write(file.read())
        except FileNotFoundError:
            # If the file is not found, send a 404 error
            return self.send_error(404)
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        # Set HTTP headers for the response
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()     

    def serve_static_files(self, path):
        # Construct the full path and serve the file
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

def run(server_class=HTTPServer, handler_class=StatisticsRequestHandler, port=8443, statistics_db=ServerStats):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # Set up an SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert/cert.pem', keyfile='cert/key.pem')  # Adjust file paths as necessary

    # Initialize database for storing statistics
    statistics_db().init_db()

    # Wrap the server socket in the context for HTTPS
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f'Starting httpd server on port {port}')
    try:
        httpd.serve_forever()
    except:
        httpd.server_close()

if __name__ == '__main__':
    run()
