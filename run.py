# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


from app import LicenseServer
import os
import sys

def main():
    # Проверка существования config.json
    if not os.path.exists('config.json'):
        print("Error: config.json not found!")
        print("Please create config.json first or run: python generate_keys.py")
        sys.exit(1)
    
    # Проверка безопасности ключей
    with open('config.json', 'r') as f:
        import json
        config = json.load(f)
    
    # Проверяем, не используются ли ключи по умолчанию
    default_keys = [
        "CHANGE_THIS_TO_RANDOM_32_BYTES_BASE64",
        "your_secret_api_key_here"
    ]
    
    security_issues = []
    if config['database']['encryption_key'] in default_keys:
        security_issues.append("Database encryption key is default")
    if config['security']['jwt_secret'] in default_keys:
        security_issues.append("JWT secret is default")
    if config['security']['hmac_secret'] in default_keys:
        security_issues.append("HMAC secret is default")
    if "your_secret_api_key_here" in config['security']['api_keys']:
        security_issues.append("API key is default")
    
    if security_issues:
        print("SECURITY WARNINGS:")
        for issue in security_issues:
            print(f"  - {issue}")
        print("\nPlease run: python generate_keys.py to generate secure keys")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Запуск сервера
    server = LicenseServer()
    print(f"Starting license server on {config['server']['host']}:{config['server']['port']}")
    server.run()

if __name__ == '__main__':
    main()