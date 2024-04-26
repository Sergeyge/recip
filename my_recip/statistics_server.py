from statistic_presentation import AuthenticatedStatsHandler, StatsServer


def run(server_class=StatsServer, handler_class=AuthenticatedStatsHandler, port=8002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Server stopped.")

if __name__ == '__main__':
    run()
