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

    def register_user(self, username, password):
        # validate username and strong  password
        if len(username) < 4:
            return False, "Username must be at least 4 characters long"
        if len(password) < 8:            
            return False, "Password must be at least 8 characters long"
 
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if the username already exists
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        if c.fetchone() is not None:
            conn.close()
            return False, "Username already exists"

        # Insert new user with hashed password
        hashed_password = self.hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return True, "User registered successfully"

    @staticmethod
    def hash_password(password):
        # Use hashlib to create a hash of the password for security reasons.
        # This is a simple implementation.
        return hashlib.sha256(password.encode()).hexdigest()
    

    # Add other user management methods as needed
