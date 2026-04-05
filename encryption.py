from cryptography.fernet import Fernet
import os
import hashlib
import logging
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KEY_FILE = "secret.key"
ENCRYPTED_FILE = "encrypted_data/encrypted.csv"
DECRYPTED_FILE = "data/decrypted.csv"

# Generate key (only once)
def generate_key():
    """Generate and save encryption key"""
    try:
        if os.path.exists(KEY_FILE):
            logger.warning(f"{KEY_FILE} already exists")
            return
        
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        logger.info(f"Key generated and saved to {KEY_FILE}")
    except Exception as e:
        logger.error(f"Failed to generate key: {e}")
        raise

# Load key with validation
def load_key():
    """Load encryption key with error handling"""
    try:
        if not os.path.exists(KEY_FILE):
            logger.error(f"{KEY_FILE} not found. Run generate_key() first.")
            raise FileNotFoundError(f"{KEY_FILE} not found")
        
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
        logger.info("Key loaded successfully")
        return key
    except Exception as e:
        logger.error(f"Failed to load key: {e}")
        raise

# Encrypt file
def encrypt_file(filename):
    """Encrypt a CSV file"""
    try:
        if not os.path.exists(filename):
            logger.error(f"Source file {filename} not found")
            raise FileNotFoundError(f"{filename} not found")
        
        key = load_key()
        f = Fernet(key)

        with open(filename, "rb") as file:
            data = file.read()

        encrypted_data = f.encrypt(data)

        os.makedirs("encrypted_data", exist_ok=True)
        with open(ENCRYPTED_FILE, "wb") as file:
            file.write(encrypted_data)
        
        logger.info(f"File encrypted: {filename} -> {ENCRYPTED_FILE}")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise

# Decrypt file
def decrypt_file():
    """Decrypt file to disk"""
    try:
        if not os.path.exists(ENCRYPTED_FILE):
            logger.error(f"Encrypted file {ENCRYPTED_FILE} not found")
            raise FileNotFoundError(f"{ENCRYPTED_FILE} not found")
        
        key = load_key()
        f = Fernet(key)

        with open(ENCRYPTED_FILE, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = f.decrypt(encrypted_data)

        os.makedirs("data", exist_ok=True)
        with open(DECRYPTED_FILE, "wb") as file:
            file.write(decrypted_data)
        
        logger.info(f"File decrypted: {ENCRYPTED_FILE} -> {DECRYPTED_FILE}")
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise

# Hash user data
def hash_data(data):
    """Hash sensitive data (user IDs, emails, etc.)"""
    try:
        if not data:
            logger.warning("Empty data provided to hash_data")
            return None
        
        hashed = hashlib.sha256(str(data).encode()).hexdigest()
        logger.info("Data hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Hashing failed: {e}")
        raise