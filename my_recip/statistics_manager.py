import sqlite3
import datetime

class ServerStats:
    def __init__(self, db_path='server_stats.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                method TEXT,
                timestamp TEXT,
                ip TEXT,
                port INTEGER,
                user_agent TEXT
            )
        ''')
        conn.commit()
        conn.close()


    def increment_request_count(self, method, client_address, user_agent):
        ip, port = client_address
        timestamp = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO requests (method, timestamp, ip, port, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (method, timestamp, ip, port, user_agent))
        conn.commit()
        conn.close()


    def report(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # General statistics
        print("Overall Statistics:")
        c.execute('SELECT method, COUNT(*) FROM requests GROUP BY method')
        methods_count = c.fetchall()
        for method, count in methods_count:
            print(f"{method}: {count}")

        c.execute('SELECT user_agent, COUNT(*) FROM requests GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 5')
        user_agents = c.fetchall()
        print("Top 5 User-Agents:")
        for user_agent, count in user_agents:
            print(f"{user_agent}: {count}")

        # Statistics per IP
        print("\nStatistics per IP:")
        c.execute('SELECT DISTINCT ip FROM requests')
        ips = c.fetchall()
        for ip in ips:
            ip = ip[0]  # Extract string from tuple
            print(f"\nStatistics for IP: {ip}")

            # Count requests per method for this IP
            c.execute('SELECT method, COUNT(*) FROM requests WHERE ip=? GROUP BY method', (ip,))
            method_counts = c.fetchall()
            for method, count in method_counts:
                print(f"  Method {method}: {count}")

            # Display top User-Agents for this IP
            c.execute('SELECT user_agent, COUNT(*) FROM requests WHERE ip=? GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 3', (ip,))
            user_agents = c.fetchall()
            print("  Top User-Agents:")
            for user_agent, count in user_agents:
                print(f"    {user_agent}: {count}")

        conn.close()

