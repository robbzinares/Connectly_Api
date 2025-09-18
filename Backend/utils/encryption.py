from cryptography.fernet import Fernet
import os

# Path where we'll store the encryption key
KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")

def load_or_create_key():
    """
    Load the encryption key from secret.key.
    If it doesn't exist, generate one.
    """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# Initialize Fernet with the loaded key
fernet = Fernet(load_or_create_key())

def encrypt_text(plain_text: str) -> str:
    """
    Encrypts plain text into a secure string.
    """
    token = fernet.encrypt(plain_text.encode())
    return token.decode()

def decrypt_text(token: str) -> str:
    """
    Decrypts a secure string back to plain text.
    """
    plain_text = fernet.decrypt(token.encode())
    return plain_text.decode()
