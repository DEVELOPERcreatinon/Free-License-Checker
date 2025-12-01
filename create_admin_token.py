# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation

import jwt
import json
from datetime import datetime, timedelta
import base64

def create_admin_token():
    """Создание JWT токена для администратора"""
    
    try:
        # Загрузка конфигурации
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        jwt_secret = config['security']['jwt_secret']
        
        # Создание полезной нагрузки
        payload = {
            'admin': True,
            'username': 'administrator',
            'created': datetime.utcnow().isoformat(),
            'exp': datetime.utcnow() + timedelta(days=365)  # Токен на 1 год
        }
        
        # Создание JWT токена
        token = jwt.encode(
            payload,
            jwt_secret,
            algorithm='HS256'
        )
        
        print("✅ Административный токен создан!")
        print(f"\n🔑 Token: {token}")
        print(f"\n📋 Пример использования в запросах:")
        print(f"   Authorization: Bearer {token}")
        
        return token
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == '__main__':
    print("=========================================")
    print("🔑 Admin Token Generator")
    print("=========================================\n")
    create_admin_token()
