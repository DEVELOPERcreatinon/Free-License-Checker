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
        print("Ошибка: config.json не найден!")
        print("Пожалуйста, создайте config.json сначала или запустите: python generate_keys.py")
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
        security_issues.append("Ключ шифрования базы данных по умолчанию")
    if config['security']['jwt_secret'] in default_keys:
        security_issues.append("JWT секрет по умолчанию")
    if config['security']['hmac_secret'] in default_keys:
        security_issues.append("HMAC секрет по умолчанию")
    if "your_secret_api_key_here" in config['security']['api_keys']:
        security_issues.append("API ключ по умолчанию")
    
    if security_issues:
        print("ПРЕДУПРЕЖДЕНИЯ БЕЗОПАСНОСТИ:")
        for issue in security_issues:
            print(f"  - {issue}")
        print("\nПожалуйста, запустите: python generate_keys.py для генерации безопасных ключей")
        response = input("Продолжить в любом случае? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Запуск сервера
    server = LicenseServer()
    print(f"Запуск сервера лицензий на {config['server']['host']}:{config['server']['port']}")
    server.run()

if __name__ == '__main__':
    main()