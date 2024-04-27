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
                user_agent TEXT,
                is_registered BOOLEAN                  
            )
        ''')
        conn.commit()
        conn.close()


    def increment_request_count(self, method, client_address, user_agent, is_registered):
        ip, port = client_address
        timestamp = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO requests (method, timestamp, ip, port, user_agent, is_registered)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (method, timestamp, ip, port, user_agent, is_registered))
        conn.commit()
        conn.close()


    def report(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        stats_data = {}

        # General statistics on request methods
        c.execute('SELECT method, COUNT(*) FROM requests GROUP BY method')
        methods_count = c.fetchall()
        stats_data['methods'] = [{'method': method, 'count': count} for method, count in methods_count]

        # Top User-Agents
        c.execute('SELECT user_agent, COUNT(*) FROM requests GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 5')
        user_agents = c.fetchall()
        stats_data['top_user_agents'] = [{'user_agent': user_agent, 'count': count} for user_agent, count in user_agents]

        # Count of requests from registered and non-registered users
        c.execute('SELECT is_registered, COUNT(*) FROM requests GROUP BY is_registered')
        registration_counts = c.fetchall()
        stats_data['registered'] = {'true': 0, 'false': 0}
        for is_registered, count in registration_counts:
            key = 'true' if is_registered else 'false'
            stats_data['registered'][key] = count

        # Statistics per IP (optional, remove if not needed)
        c.execute('SELECT DISTINCT ip FROM requests')
        ips = c.fetchall()
        ips_stats = []
        for ip in ips:
            ip = ip[0]  # Extract string from tuple
            ip_data = {'ip': ip, 'details': {}}
            c.execute('SELECT method, COUNT(*) FROM requests WHERE ip=? GROUP BY method', (ip,))
            ip_data['details']['methods'] = [{'method': method, 'count': count} for method, count in c.fetchall()]
            c.execute('SELECT user_agent, COUNT(*) FROM requests WHERE ip=? GROUP BY user_agent ORDER BY COUNT(*) DESC LIMIT 5', (ip,))
            ip_data['details']['user_agents'] = [{'user_agent': user_agent, 'count': count} for user_agent, count in c.fetchall()]
            ips_stats.append(ip_data)
        
        stats_data['ips'] = ips_stats
        conn.close()
        return stats_data


        stats_data['ips'] = ips_stats
        conn.close()
        return stats_data