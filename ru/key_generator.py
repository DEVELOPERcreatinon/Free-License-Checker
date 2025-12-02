# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


from database import DatabaseManager
from security import SecurityManager
import json
from datetime import datetime

class KeyGenerator:
    def __init__(self, config, security_manager, db_manager):
        self.config = config
        self.security = security_manager
        self.db = db_manager
        self.prefixes = {
            "BUSINESS": "BUS",
            "PRO": "PRO", 
            "STUDENT": "STU"
        }
    
    def generate_keys_for_all_types(self):
        """Генерация ключей для всех типов лицензий"""
        results = {}
        
        for license_type in self.config['licensing']['license_types']:
            results[license_type] = self.generate_keys_for_type(
                license_type, 
                self.config['licensing']['keys_per_type']
            )
        
        return results
    
    def generate_keys_for_type(self, license_type, count):
        """Генерация ключей для конкретного типа лицензии"""
        generated_keys = []
        success_count = 0
        
        for i in range(count):
            # Генерируем ключ с префиксом
            key = self.generate_prefixed_key(license_type)
            
            # Используем default_validity_days из конфигурации
            validity_days = self.config['licensing']['default_validity_days']
            
            if self.db.add_license_key(key, license_type, validity_days):
                generated_keys.append(key)
                success_count += 1
        
        return {
            'success_count': success_count,
            'total_attempted': count,
            'keys': generated_keys
        }
    
    def generate_prefixed_key(self, license_type):
        """Генерация ключа с префиксом соответствующего типа"""
        prefix = self.prefixes.get(license_type, "")
        prefix_length = len(prefix)
        
        # Генерируем основную часть ключа (общая длина минус длина префикса)
        main_key_length = self.config['licensing']['key_length'] - prefix_length
        main_part = self.security.generate_secure_key(main_key_length)
        
        # Комбинируем префикс и основную часть
        return prefix + main_part