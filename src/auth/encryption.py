"""
Session data encryption module for NFR-5.1 compliance.

Provides encryption/decryption for sensitive session data at rest using Fernet (AES-128).
"""

import json
import logging
import os
from typing import Any, Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption/decryption operations fail."""
    pass


class SessionDataEncryptor:
    """
    Handles encryption and decryption of sensitive session data.

    Uses Fernet (symmetric encryption with AES-128 in CBC mode) for data at rest encryption.
    Key is loaded from environment variable SESSION_ENCRYPTION_KEY or generated if not set.

    Encrypted fields:
    - stage_data: All interview responses and business analysis
    - conversation_history: User interaction history
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize encryptor with encryption key.

        Args:
            encryption_key: 32-byte URL-safe base64-encoded key. If None, loads from env or generates.
        """
        if encryption_key is None:
            # Try to load from environment
            key_str = os.environ.get("SESSION_ENCRYPTION_KEY")
            if key_str:
                encryption_key = key_str.encode()
                logger.info("Loaded encryption key from environment")
            else:
                # Generate a new key for development (SHOULD BE SET IN PRODUCTION)
                encryption_key = Fernet.generate_key()
                logger.warning(
                    "SESSION_ENCRYPTION_KEY not set - generated temporary key. "
                    "Set SESSION_ENCRYPTION_KEY in production!"
                )

        try:
            self.cipher = Fernet(encryption_key)
            self.encryption_key = encryption_key
            logger.info("SessionDataEncryptor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryptor: {e}")
            raise EncryptionError(f"Invalid encryption key: {e}") from e

    def encrypt_dict(self, data: dict[Any, Any]) -> str:
        """
        Encrypt a dictionary to a base64-encoded string.

        Args:
            data: Dictionary to encrypt

        Returns:
            Base64-encoded encrypted string

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Serialize to JSON
            json_data = json.dumps(data)
            # Encrypt
            encrypted_bytes = self.cipher.encrypt(json_data.encode())
            # Return as string for database storage
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise EncryptionError(f"Encryption failed: {e}") from e

    def decrypt_dict(self, encrypted_data: str) -> dict[Any, Any]:
        """
        Decrypt a base64-encoded string back to a dictionary.

        Args:
            encrypted_data: Base64-encoded encrypted string

        Returns:
            Decrypted dictionary

        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            # Deserialize from JSON
            json_data = decrypted_bytes.decode()
            return json.loads(json_data)
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise EncryptionError(f"Decryption failed: {e}") from e

    def encrypt_list(self, data: list[Any]) -> str:
        """
        Encrypt a list to a base64-encoded string.

        Args:
            data: List to encrypt

        Returns:
            Base64-encoded encrypted string

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Serialize to JSON
            json_data = json.dumps(data)
            # Encrypt
            encrypted_bytes = self.cipher.encrypt(json_data.encode())
            # Return as string for database storage
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt list: {e}")
            raise EncryptionError(f"Encryption failed: {e}") from e

    def decrypt_list(self, encrypted_data: str) -> list[Any]:
        """
        Decrypt a base64-encoded string back to a list.

        Args:
            encrypted_data: Base64-encoded encrypted string

        Returns:
            Decrypted list

        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            # Deserialize from JSON
            json_data = decrypted_bytes.decode()
            return json.loads(json_data)
        except Exception as e:
            logger.error(f"Failed to decrypt list: {e}")
            raise EncryptionError(f"Decryption failed: {e}") from e


# Global encryptor instance (initialized once per process)
_encryptor: Optional[SessionDataEncryptor] = None


def get_encryptor() -> SessionDataEncryptor:
    """
    Get or create the global SessionDataEncryptor instance.

    Returns:
        SessionDataEncryptor: Global encryptor instance
    """
    global _encryptor
    if _encryptor is None:
        _encryptor = SessionDataEncryptor()
    return _encryptor
