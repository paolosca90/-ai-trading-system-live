import os
from cryptography.fernet import Fernet
import json
import base64
from typing import Dict, Any

class CredentialsEncryption:
    """Utility class for encrypting/decrypting MT5 credentials"""

    def __init__(self):
        secret_key = os.getenv("MT5_SECRET_KEY")
        if not secret_key:
            raise ValueError("MT5_SECRET_KEY environment variable not set")

        # Ensure key is 32 bytes and base64 encoded
        if len(secret_key) < 32:
            # Pad with zeros if too short
            secret_key = secret_key.ljust(32, '0')
        elif len(secret_key) > 32:
            # Truncate if too long
            secret_key = secret_key[:32]

        # Convert to base64 for Fernet
        key_bytes = base64.urlsafe_b64encode(secret_key.encode())
        self.cipher_suite = Fernet(key_bytes)

    def encrypt_credentials(self, login: int, password: str, server: str) -> str:
        """Encrypt MT5 credentials"""
        credentials = {
            "login": login,
            "password": password,
            "server": server
        }

        # Convert to JSON and encrypt
        json_str = json.dumps(credentials)
        encrypted_data = self.cipher_suite.encrypt(json_str.encode())
        return encrypted_data.decode()

    def decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Decrypt MT5 credentials"""
        try:
            # Decrypt and parse JSON
            decrypted_data = self.cipher_suite.decrypt(encrypted_credentials.encode())
            credentials = json.loads(decrypted_data.decode())
            return credentials
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")

# Global encryption instance
credentials_crypto = CredentialsEncryption()
