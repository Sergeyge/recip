from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import base64

from statistics_manager import ServerStats

class AuthenticatedStatsHandler(SimpleHTTPRequestHandler):
    # Username and password for demonstration purposes
    USERNAME = 'admin'
    PASSWORD = 'password'

    def do_GET(self):
        if self.path == '/stats':
            if self.authenticate():
                self.serve_stats_page()
            else:
                self.send_auth_request()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            credentials = parse_qs(post_data)
            username = credentials.get('username', [None])[0]
            password = credentials.get('password', [None])[0]

            if username == self.USERNAME and password == self.PASSWORD:
                self.send_response(301)
                self.send_header('Location', '/stats')
                self.send_header('Set-Cookie', 'session=Valid')
                self.end_headers()
            else:
                self.send_auth_request()
        else:
            super().do_POST()

    def authenticate(self):
        if "Cookie" in self.headers:
            cookies = self.headers['Cookie']
            return 'session=Valid' in cookies
        return False

    def send_auth_request(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Stats"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>401 Unauthorized</h1><p>You must login to view this page.</p></body></html>')

    def serve_stats_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        stats_data = self.server.stats.report()  # Assume there is a report method returning HTML data
        self.wfile.write(f"<html><body><h1>Server Statistics</h1>{stats_data}</body></html>".encode())

class StatsServer(HTTPServer):
    def __init__(self, server_address, handler_class=AuthenticatedStatsHandler):
        super().__init__(server_address, handler_class)
        self.stats = ServerStats()  # Assume ServerStats is properly defined elsewhere
