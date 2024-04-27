from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import ssl
from urllib.parse import urlparse, parse_qs
from statistics_manager import ServerStats

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    stats_manager = ServerStats()  # Assuming you've imported ServerStats


    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        if path == '/':
            self.serve_file('statistics/index.html', 'text/html')
        elif path.startswith('/statistics/'):
            self.serve_static_files(path)
        elif self.path == '/api/statistics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = self.stats_manager.report()
            self.wfile.write(json.dumps(stats).encode())
        else:
            super().do_GET()  # Handle other GET requests normally

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self._set_headers(200, content_type)
                self.wfile.write(file.read())
        except FileNotFoundError:
            return self.send_error(404)
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()     

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


    # Add other methods and functionalities as needed
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8443):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # Set up an SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert/cert.pem', keyfile='cert/key.pem')  # Adjust file paths as necessary

    # Wrap the server socket in the context
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f'Starting httpd server on port {port}')
    try:
        httpd.serve_forever()
    except:
        httpd.server_close()
if __name__ == '__main__':
    run()
