import sqlite3
import datetime

# Class to manage server statistics
class ServerStats:
    # Initialize the database path
    def __init__(self, db_path='server_stats.db'):
        self.db_path = db_path
    
    # Initialize the database
    def init_db(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Create the requests table if it does not exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                method TEXT,
                timestamp TEXT,
                ip TEXT,
                port INTEGER,
                user_agent TEXT,
                api TEXT,
                is_registered BOOLEAN                  
            )
        ''')
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        print('Statistic Database initialized')

    # Method to increment the request count
    def increment_request_count(self, method, client_address, user_agent, api, is_registered):
        ip, port = client_address
        # Get the current time
        timestamp = datetime.datetime.now().isoformat()
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Insert the request data into the requests table
        c.execute('''
            INSERT INTO requests (method, timestamp, ip, port, user_agent, api, is_registered)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (method, timestamp, ip, port, user_agent, api, is_registered))
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    # Method to generate statistics report
    def report(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Dictionary to store the statistics data
        stats_data = {} 

        # General statistics on request methods
        c.execute('SELECT method, COUNT(*) FROM requests GROUP BY method')
        methods_count = c.fetchall()
        stats_data['methods'] = [{'method': method, 'count': count} for method, count in methods_count]

        # API usage statistics, simplified to count total requests per API only
        c.execute('''
            SELECT api, COUNT(*) AS total_requests
            FROM requests
            GROUP BY api
        ''')
        api_stats = c.fetchall()
        # Convert the data to a list of dictionaries
        stats_data['api_usage'] = [{'api': api, 'total_requests': total}
                                for api, total in api_stats]
        # Top 5 user agents by request count
        c.execute('SELECT user_agent, COUNT(*) FROM requests GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 5')
        user_agents = c.fetchall()
        # Convert the data to a list of dictionaries
        stats_data['top_user_agents'] = [{'user_agent': user_agent, 'count': count} for user_agent, count in user_agents]

        # Count of requests from registered and non-registered users
        c.execute('SELECT is_registered, COUNT(*) FROM requests GROUP BY is_registered')
        registration_counts = c.fetchall()
        # Initialize the dictionary with default values
        stats_data['registered'] = {'true': 0, 'false': 0}
        # Update the dictionary with the actual counts
        for is_registered, count in registration_counts:
            key = 'true' if is_registered else 'false'
            stats_data['registered'][key] = count

        # Statistics on per IP addresses
        c.execute('SELECT DISTINCT ip FROM requests')
        ips = c.fetchall()
        ips_stats = []
        for ip in ips:
            # Extract the IP address
            ip = ip[0]  
            # Dictionary to store IP address details
            ip_data = {'ip': ip, 'details': {}}
            # Total number of requests from the IP address
            c.execute('SELECT method, COUNT(*) FROM requests WHERE ip=? GROUP BY method', (ip,))
            # List of dictionaries with method and count
            ip_data['details']['methods'] = [{'method': method, 'count': count} for method, count in c.fetchall()]
            # Top 5 user agents from the IP address
            c.execute('SELECT user_agent, COUNT(*) FROM requests WHERE ip=? GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 5', (ip,))
            # List of dictionaries with user agent and count
            ip_data['details']['user_agents'] = [{'user_agent': user_agent, 'count': count} for user_agent, count in c.fetchall()]
            # Add the IP data to the list
            ips_stats.append(ip_data)
        # store the IP statistics in the main dictionary
        stats_data['ips'] = ips_stats
        # Close the connection
        conn.close()
        # Return the statistics data
        return stats_data