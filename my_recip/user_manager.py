import sqlite3
import hashlib

class UserManager:
    def __init__(self, db_path='users.db'):
        self._logged_in=False
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL  -- Store hashed passwords
            )
        ''')

        conn.commit()

        # Check if the default admin user exists
        c.execute('SELECT * FROM users WHERE username=?', ('admin',))
        if c.fetchone() is None:
            # Insert default admin user
            hashed_password = self.hash_password('admin')
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', hashed_password))
            conn.commit()
        conn.close()

    def check_credentials(self, username, password):
        password = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None

    def set_logged_in(self, value):
        self._logged_in = value


    @staticmethod
    def hash_password(password):
        # Use hashlib to create a hash of the password for security reasons.
        # This is a simple implementation.
        return hashlib.sha256(password.encode()).hexdigest()

    # Add other user management methods as needed
