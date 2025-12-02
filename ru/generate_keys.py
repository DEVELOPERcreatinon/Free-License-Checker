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
    """Генерация безопасного ключа заданной длины в base64"""
    random_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8')

def generate_api_key():
    """Генерация API ключа"""
    return "sk_live_" + secrets.token_hex(24)

def generate_config():
    """Генерация нового конфигурационного файла с безопасными ключами"""
    
    # Загрузка существующего конфига если он есть, иначе создание базового
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("📄 Обнаружен существующий config.json, обновляю только ключи...")
    else:
        print("📄 Создаю новый config.json...")
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
    
    # Генерация безопасных ключей
    print("🔐 Генерация безопасных ключей...")
    
    # Ключ шифрования базы данных (32 байта)
    config['database']['encryption_key'] = generate_secure_key(32)
    print(f"  ✓ Ключ шифрования базы данных: {config['database']['encryption_key'][:20]}...")
    
    # JWT секрет (32 байта)
    config['security']['jwt_secret'] = generate_secure_key(32)
    print(f"  ✓ JWT секрет: {config['security']['jwt_secret'][:20]}...")
    
    # HMAC секрет (32 байта)
    config['security']['hmac_secret'] = generate_secure_key(32)
    print(f"  ✓ HMAC секрет: {config['security']['hmac_secret'][:20]}...")
    
    # API ключи (генерируем 3 ключа)
    config['security']['api_keys'] = [
        generate_api_key(),
        generate_api_key(),
        generate_api_key()
    ]
    print(f"  ✓ API ключи: {len(config['security']['api_keys'])} ключей сгенерировано")
    print(f"    • {config['security']['api_keys'][0]}")
    
    # Сохранение конфигурации
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Конфигурационный файл успешно создан/обновлен!")
    print(f"📁 Файл: config.json")
    print(f"\n⚠️  ВАЖНО: Сохраните эти ключи в безопасном месте!")
    print(f"   Они понадобятся для восстановления доступа к данным.")
    
    # Генерация административного JWT токена
    print(f"\n🔑 Для создания административного JWT токена выполните:")
    print(f"   python create_admin_token.py")

def main():
    print("=========================================")
    print("🔐 Генератор ключей сервера лицензий")
    print("=========================================\n")
    
    print("Этот скрипт сгенерирует безопасные ключи для вашего сервера лицензий.")
    print("Все ключи будут случайными и уникальными.\n")
    
    if os.path.exists('config.json'):
        print("⚠️  Предупреждение: Существующий config.json будет перезаписан!")
        response = input("Продолжить? (y/N): ")
        if response.lower() != 'y':
            print("❌ Отменено пользователем.")
            return
    
    generate_config()

if __name__ == '__main__':
    main()