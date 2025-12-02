# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation

import secrets
import base64
import json
import os
from cryptography.fernet import Fernet

def generate_secure_key(length=32):
    """Generate secure key of given length in base64"""
    random_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')

def generate_api_key():
    """Generate API key"""
    return "sk_live_" + secrets.token_hex(24)

def generate_config():
    """Generate new configuration file with secure keys"""
    
    # Load existing config if exists, otherwise create base config
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("📄 Existing config.json detected, updating only keys...")
    else:
        print("📄 Creating new config.json...")
        config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "ssl_enabled": True,
                "ssl_cert_path": "cert.pem",
                "ssl_key_path": "key.pem"
            },
            "database": {
                "type": "sqlite",
                "filename": "licenses.db",
                "encryption_key": "CHANGE_THIS_TO_RANDOM_32_BYTES_BASE64",
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "security": {
                "api_key_required": True,
                "api_keys": ["your_secret_api_key_here"],
                "rate_limiting_enabled": True,
                "max_requests_per_minute": 600,
                "jwt_secret": "CHANGE_THIS_TO_RANDOM_32_BYTES_BASE64",
                "jwt_expiration_hours": 24,
                "hmac_secret": "CHANGE_THIS_TO_RANDOM_32_BYTES_BASE64",
                "require_encrypted_communication": True,
                "allowed_ips": [],
                "blocked_ips": []
            },
            "licensing": {
                "key_length": 16,
                "key_format": "alphanumeric",
                "auto_generate_keys": True,
                "keys_per_type": 100,
                "default_validity_days": 30,
                "license_types": ["BUSINESS", "PRO", "STUDENT"],
                "allow_multiple_activations": False,
                "max_activations_per_key": 1
            },
            "rate_limiting": {
                "storage_uri": "memory://",
                "strategy": "fixed-window",
                "storage_options": {}
            },
            "logging": {
                "level": "INFO",
                "file": "license_server.log",
                "max_file_size_mb": 100,
                "backup_count": 5,
                "log_requests": True,
                "log_errors": True
            }
        }
    
    # Generate secure keys
    print("🔐 Generating secure keys...")
    
    # Database encryption key (32 bytes)
    config['database']['encryption_key'] = generate_secure_key(32)
    print(f"  ✓ Database encryption key: {config['database']['encryption_key'][:20]}...")
    
    # JWT secret (32 bytes)
    config['security']['jwt_secret'] = generate_secure_key(32)
    print(f"  ✓ JWT secret: {config['security']['jwt_secret'][:20]}...")
    
    # HMAC secret (32 bytes)
    config['security']['hmac_secret'] = generate_secure_key(32)
    print(f"  ✓ HMAC secret: {config['security']['hmac_secret'][:20]}...")
    
    # API keys (generate 3 keys)
    config['security']['api_keys'] = [
        generate_api_key(),
        generate_api_key(),
        generate_api_key()
    ]
    print(f"  ✓ API keys: {len(config['security']['api_keys'])} keys generated")
    print(f"    • {config['security']['api_keys'][0]}")
    
    # Save configuration
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration file successfully created/updated!")
    print(f"📁 File: config.json")
    print(f"\n⚠️  IMPORTANT: Save these keys in a secure place!")
    print(f"   They will be needed to restore access to data.")
    
    # Generate administrative JWT token
    print(f"\n🔑 To create administrative JWT token, run:")
    print(f"   python create_admin_token.py")

def main():
    print("=========================================")
    print("🔐 License Server Key Generator")
    print("=========================================\n")
    
    print("This script will generate secure keys for your license server.")
    print("All keys will be random and unique.\n")
    
    if os.path.exists('config.json'):
        print("⚠️  Warning: Existing config.json will be overwritten!")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled by user.")
            return
    
    generate_config()

if __name__ == '__main__':
    main()