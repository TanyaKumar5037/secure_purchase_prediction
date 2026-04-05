from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import logging
from functools import wraps
from flask import session, redirect, url_for

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERS_FILE = "users.json"

# Initialize users file if it doesn't exist
def init_users():
    """Create users.json with default admin account"""
    try:
        if not os.path.exists(USERS_FILE):
            default_users = {
                "admin": {
                    "password": generate_password_hash("admin123"),
                    "email": "admin@secure.com",
                    "created": "2026-04-05"
                }
            }
            with open(USERS_FILE, "w") as f:
                json.dump(default_users, f, indent=2)
            logger.info(f"Users file created with default admin account")
        else:
            logger.info("Users file already exists")
    except Exception as e:
        logger.error(f"Failed to initialize users: {e}")
        raise

# Load users from file
def load_users():
    """Load all users from JSON file"""
    try:
        if not os.path.exists(USERS_FILE):
            init_users()
        
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        logger.info("Users loaded successfully")
        return users
    except Exception as e:
        logger.error(f"Failed to load users: {e}")
        return {}

# Save users to file
def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        logger.info("Users saved successfully")
    except Exception as e:
        logger.error(f"Failed to save users: {e}")
        raise

# Register new user
def register_user(username, password, email):
    """Register a new user"""
    try:
        if not username or not password or not email:
            logger.warning("Registration: Missing required fields")
            return False, "All fields are required"
        
        if len(username) < 3:
            logger.warning("Registration: Username too short")
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            logger.warning("Registration: Password too short")
            return False, "Password must be at least 6 characters"
        
        users = load_users()
        
        if username in users:
            logger.warning(f"Registration: Username '{username}' already exists")
            return False, "Username already exists"
        
        users[username] = {
            "password": generate_password_hash(password),
            "email": email,
            "created": "2026-04-05"
        }
        
        save_users(users)
        logger.info(f"User '{username}' registered successfully")
        return True, "Registration successful"
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return False, str(e)

# Login user
def login_user(username, password):
    """Verify user credentials"""
    try:
        if not username or not password:
            logger.warning("Login: Missing credentials")
            return False, "Username and password required"
        
        users = load_users()
        
        if username not in users:
            logger.warning(f"Login: User '{username}' not found")
            return False, "Invalid username or password"
        
        user = users[username]
        
        if not check_password_hash(user["password"], password):
            logger.warning(f"Login: Invalid password for user '{username}'")
            return False, "Invalid username or password"
        
        logger.info(f"User '{username}' logged in successfully")
        return True, "Login successful"
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False, str(e)

# Decorator to protect routes
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            logger.warning("Access denied: User not logged in")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Get current user
def get_current_user():
    """Get the currently logged-in user"""
    return session.get("username")

# Logout user
def logout_user():
    """Clear user session"""
    try:
        username = session.get("username")
        if username:
            logger.info(f"User '{username}' logged out")
        session.clear()
        return True
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return False