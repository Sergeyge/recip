import sqlite3
import hashlib
import re

def is_valid_email(email):
    """ Validate email format using regular expression. """
    return re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$', email) is not None

def is_valid_password(password):
    """ Validate password format using regular expression. """
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$', password) is not None

class UserManager:
    def __init__(self, db_path='recipes.db'):
        self._logged_in=False
        self._user_id=None
        self.db_path = db_path

    def check_credentials(self, username, password):
        password = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        self._user_id = user[0] if user else None
        return user[0] if user else None

    def set_logged_in(self, value):
        self._logged_in = value

    def register_user(self, username, password, email, role='viewer'):
        if not is_valid_email(email):
            return False, "Invalid email format"
        
        if not is_valid_password(password):
            return False, "Password does not meet the requirements"    
         
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if the username already exists
        c.execute('SELECT * FROM users WHERE username=? OR email=?', (username, email))
        if c.fetchone():
            conn.close()
            return False, "Username or email already exists"

        # Insert new user with hashed password and role
        hashed_password = self.hash_password(password)
        c.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', (username, hashed_password, email, role))
        conn.commit()
        conn.close()
        return True, "User registered successfully"

    @staticmethod
    def hash_password(password):
        # Use hashlib to create a hash of the password for security reasons.
        # This is a simple implementation.
        return hashlib.sha256(password.encode()).hexdigest()
    

    # Add other user management methods as needed
