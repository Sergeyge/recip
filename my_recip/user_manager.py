import sqlite3
import hashlib
import re
from Init_Recipe_DB import RecipeDbManager

# Email and password validation functions
def is_valid_email(email):
    # Validate email format using regular expression.
    return re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$', email) is not None

def is_valid_password(password):
    # Validate password format using regular expression.
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$', password) is not None

# class UserManager to manage user authentication and registration
class UserManager:
    def __init__(self):
        # Initialize the user manager with logged_in false and user_id set to None
        self._logged_in=False
        self._user_id=None
        # Get the database path from RecipeDbManager
        self.db_path = RecipeDbManager().db_path

    # check_credentials method to check if the username and password are valid
    def check_credentials(self, username, password):
        # Hash the password using sha256
        password = self.hash_password(password)
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if the username and password match
        c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        # Close the connection
        conn.close()
        # If user exists, set the user_id and logged_in to True
        self._user_id = user[0] if user else None
        # Return the user_id if user exists else None
        return user[0] if user else None

    # Setter and for user_id
    def set_logged_in(self, value):
        self._logged_in = value

    # Method to register a new user
    def register_user(self, username, password, email, role='viewer'):
        # Check if the email and password are valid
        if not is_valid_email(email):
            return False, "Invalid email format"
        if not is_valid_password(password):
            return False, "Password does not meet the requirements"    
        
        # Connect to the database
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
        # Commit the changes to the database
        conn.commit()
        # Close the connection
        conn.close()
        # Return True and success message if user is registered successfully
        return True, "User registered successfully"

    # hash_password static method to hash the password using sha256
    @staticmethod
    def hash_password(password):
        # Use hashlib to create a hash of the password for security reasons.
        # This is a simple implementation.
        return hashlib.sha256(password.encode()).hexdigest()

