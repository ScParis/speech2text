"""
Configuration Manager for Speech-to-Text Transcriber

This module provides secure storage and management of API credentials and other
configuration settings. It uses Fernet symmetric encryption to protect sensitive data.

Features:
- Secure storage of API credentials
- Automatic encryption key management
- Environment variable integration
- Error handling and logging

Usage:
    config_manager = ConfigManager()
    
    # Save configuration
    config_manager.save_config({
        'GEMINI_API_KEY': 'your-api-key',
        'GEMINI_API_URL': 'https://api.example.com'
    })
    
    # Load configuration
    config = config_manager.load_config()
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import logging

class ConfigManager:
    """Manages secure storage of API tokens and configuration."""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), '.config.enc')
        self._init_encryption_key()
        
    def _init_encryption_key(self):
        """Initialize or load the encryption key."""
        key_file = os.path.join(os.path.dirname(__file__), '.key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            # Generate a new key
            salt = b'speech2text'  # Fixed salt for this application
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
            # Save the key
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher_suite = Fernet(self.key)
    
    def save_config(self, config_data):
        """Save configuration data securely."""
        try:
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(json.dumps(config_data).encode())
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            # Update environment variables
            if 'GEMINI_API_KEY' in config_data:
                os.environ['GEMINI_API_KEY'] = config_data['GEMINI_API_KEY']
            if 'GEMINI_API_URL' in config_data:
                os.environ['GEMINI_API_URL'] = config_data['GEMINI_API_URL']
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            return False
    
    def load_config(self):
        """Load configuration data."""
        try:
            if not os.path.exists(self.config_file):
                return {}
            
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            
            # Update environment variables
            if 'GEMINI_API_KEY' in config_data:
                os.environ['GEMINI_API_KEY'] = config_data['GEMINI_API_KEY']
            if 'GEMINI_API_URL' in config_data:
                os.environ['GEMINI_API_URL'] = config_data['GEMINI_API_URL']
            
            return config_data
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return {}
