from cryptography.fernet import Fernet
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryptor:
    def __init__(self):
        self.key = self._get_or_generate_key()
        self.fernet = Fernet(self.key)

    def _get_or_generate_key(self):
        # Use Flask secret key to derive encryption key
        secret_key = os.environ.get('FLASK_SECRET_KEY').encode()
        salt = b'pdf_flipbook_salt'  # Constant salt for consistent key derivation
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
        return key

    def encrypt(self, data):
        if data is None:
            return None
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        if encrypted_data is None:
            return None
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Global encryptor instance
encryptor = Encryptor()
