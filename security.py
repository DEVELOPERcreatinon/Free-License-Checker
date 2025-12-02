# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


import hashlib
import hmac
import base64
import secrets
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.fernet = self._setup_encryption()
        self.prefixes = {
            "BUSINESS": "BUS",
            "PRO": "PRO", 
            "STUDENT": "STU"
        }
        
    def _setup_encryption(self):
        """Setup encryption for database"""
        encryption_key = self.config['database']['encryption_key']
        if encryption_key == "CHANGE_THIS_TO_RANDOM_32_BYTES_BASE64":
            raise ValueError("Please change the encryption key in config.json")
        
        # Decode key from base64
        key = base64.urlsafe_b64decode(encryption_key)
        return Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt_data(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.fernet.decrypt(encrypted_data).decode()
    
    def generate_secure_key(self, length=16):
        """Generate secure key"""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_key_format(self, key, license_type):
        """Validate key format considering prefix"""
        expected_length = self.config['licensing']['key_length']
        
        # Check total length
        if len(key) != expected_length:
            return False
        
        # Check prefix
        prefix = self.prefixes.get(license_type, "")
        if prefix and not key.startswith(prefix):
            return False
        
        # Check that remaining part consists of allowed characters
        main_part = key[len(prefix):]
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return all(char in alphabet for char in main_part)
    
    def create_hmac_signature(self, data):
        """Create HMAC signature"""
        if isinstance(data, str):
            data = data.encode()
        hmac_secret = self.config['security']['hmac_secret'].encode()
        return hmac.new(hmac_secret, data, hashlib.sha256).hexdigest()
    
    def verify_hmac_signature(self, data, signature):
        """Verify HMAC signature"""
        expected_signature = self.create_hmac_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def create_jwt_token(self, payload):
        """Create JWT token"""
        payload['exp'] = datetime.utcnow() + timedelta(
            hours=self.config['security']['jwt_expiration_hours']
        )
        payload['iat'] = datetime.utcnow()
        return jwt.encode(
            payload, 
            self.config['security']['jwt_secret'], 
            algorithm='HS256'
        )
    
    def verify_jwt_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.config['security']['jwt_secret'], 
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def hash_key(self, key):
        """Hash license key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()