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
    """Create JWT token for administrator"""
    
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        jwt_secret = config['security']['jwt_secret']
        
        # Create payload
        payload = {
            'admin': True,
            'username': 'administrator',
            'created': datetime.utcnow().isoformat(),
            'exp': datetime.utcnow() + timedelta(days=365)  # Token valid for 1 year
        }
        
        # Create JWT token
        token = jwt.encode(
            payload,
            jwt_secret,
            algorithm='HS256'
        )
        
        print("✅ Administrative token created!")
        print(f"\n🔑 Token: {token}")
        print(f"\n📋 Usage example in requests:")
        print(f"   Authorization: Bearer {token}")
        
        return token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    print("=========================================")
    print("🔑 Admin Token Generator")
    print("=========================================\n")
    create_admin_token()