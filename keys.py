# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


import json
from database import DatabaseManager
from security import SecurityManager
from key_generator import KeyGenerator

def generate_keys_locally():
    """Локальная генерация ключей без HTTP запросов"""
    print("=== Local Key Generator ===\n")
    
    try:
        # Загрузка конфигурации
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Инициализация менеджеров
        security = SecurityManager(config)
        db = DatabaseManager(config, security)
        generator = KeyGenerator(config, security, db)
        
        # Генерация ключей
        print("Generating license keys locally...")
        results = generator.generate_keys_for_all_types()
        
        # Вывод результатов
        print("\n✅ Keys generated successfully!")
        print("\n📊 Generation Results:")
        
        total_generated = 0
        all_keys = {}
        
        for license_type, result in results.items():
            print(f"\n{license_type}:")
            print(f"  Success: {result['success_count']}/{result['total_attempted']}")
            print(f"  Keys: {', '.join(result['keys'][:5])}")  # Показываем первые 5 ключей
            if len(result['keys']) > 5:
                print(f"  ... and {len(result['keys']) - 5} more")
            
            total_generated += result['success_count']
            all_keys[license_type] = result['keys']
        
        print(f"\n🎉 Total keys generated: {total_generated}")
        
        # Сохранение ключей в файл
        output_file = 'generated_keys.json'
        with open(output_file, 'w') as f:
            json.dump(all_keys, f, indent=2)
        print(f"\n💾 All keys saved to: {output_file}")
        
        # Показать пример использования
        print(f"\n🔑 Example keys with prefixes:")
        for license_type in all_keys.keys():
            if all_keys[license_type]:
                prefix = generator.prefixes.get(license_type, "")
                print(f"  {license_type}: {all_keys[license_type][0]} (starts with '{prefix}')")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    generate_keys_locally()