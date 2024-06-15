import socket
import threading
import re
import os
import json
import ssl
from statistics_manager import ServerStats

IP = '0.0.0.0'
PORT = 8443
SOCKET_TIMEOUT = 60
HTTP_OK = 'HTTP/1.1 200 OK'
HTTP_NOT_FOUND = 'HTTP/1.1 404 Not Found'
HTTP_INTERNAL_SERVER_ERROR = 'HTTP/1.1 500 Internal Server Error'
HTTP_NOT_IMPLEMENTED_ERROR = 'HTTP/1.1 501 Not Implemented'
NL = '\r\n'
CONTENT_LEN = 'Content-Length: '
CONTENT_TYPE = 'Content-Type: '
DNL = NL + NL
ROOT = 'statistics'

# Dictionary to map file extensions to MIME types
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.htm': 'text/html; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.js': 'text/javascript; charset=UTF-8',
    '.css': 'text/css',
    '.json': 'application/json; charset=utf-8',
}

DEFAULT_FILE = '/index.html'  # Default file to serve when root is accessed

def get_file_data(filename):
    path = os.path.join(ROOT, filename.lstrip('/'))
    if os.path.exists(path):
        mode = 'rb' if any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']) else 'r'
        with open(path, mode) as file:
            return file.read()
    return None

def validate_http_request(request):
    lines = request.split("\r\n")
    if lines and len(lines) > 0:
        request_line = lines[0]
        match = re.match(r"^(GET) (/.*) HTTP/1\.1$", request_line)
        if match:
            return True, match.group(2)
    return False, None

def handle_api_request(client_socket):
    stats_manager = ServerStats()
    response_body = json.dumps(stats_manager.report())
    response_headers = f"{HTTP_OK}{NL}{CONTENT_LEN}{len(response_body)}{NL}{CONTENT_TYPE}application/json{DNL}"
    client_socket.sendall(response_headers.encode() + response_body.encode())

def handle_client(client_socket):
    print('Client connected')
    client_socket.settimeout(SOCKET_TIMEOUT)

    try:
        client_request = client_socket.recv(1024).decode('utf-8')
        if not client_request:
            return

        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print(f'Got a valid HTTP request for resource: {resource}')
            if resource.startswith('/api/statistics'):
                handle_api_request(client_socket)
            else:
                # Serve default file if root is requested
                if resource == '/':
                    resource = DEFAULT_FILE

                resource_type = os.path.splitext(resource)[1]
                data_type = MIME_TYPES.get(resource_type, 'text/html; charset=utf-8')
                data = get_file_data(resource)
                
                if data is not None:
                    if isinstance(data, bytes):
                        response_headers = f"{HTTP_OK}{NL}{CONTENT_LEN}{len(data)}{NL}{CONTENT_TYPE}{data_type}{DNL}"
                        client_socket.sendall(response_headers.encode() + data)
                    else:
                        response_headers = f"{HTTP_OK}{NL}{CONTENT_LEN}{len(data)}{NL}{CONTENT_TYPE}{data_type}{DNL}"
                        client_socket.sendall(response_headers.encode() + data.encode())
                else:
                    response = f"{HTTP_NOT_FOUND}{DNL}"
                    client_socket.sendall(response.encode())
        else:
            print('Error: Not a supported HTTP request')
            response = f"{HTTP_NOT_IMPLEMENTED_ERROR}{DNL}"
            client_socket.sendall(response.encode())
    except socket.timeout:
        print("Socket timed out")
    except Exception as e:
        print(f"Error handling client: {e}")
        response = f"{HTTP_INTERNAL_SERVER_ERROR}{DNL}"
        client_socket.sendall(response.encode())
    finally:
        print('Closing connection')
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print(f"Listening for connections on port {PORT}")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert/cert.pem', keyfile='cert/key.pem')  # Adjust file paths as necessary

    # Wrap the server socket in the context for HTTPS
    server_socket = context.wrap_socket(server_socket, server_side=True)

    # Initialize database for storing statistics
    statistics_db = ServerStats
    statistics_db().init_db()

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print('New connection received from', client_address)
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except socket.error as socketerror:
            print("Error accepting new connection: ", socketerror)
        except KeyboardInterrupt:
            print("Server shutting down.")
            break

    server_socket.close()

if __name__ == "__main__":
    main()
