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
    print("=== Локальный генератор ключей ===\n")
    
    try:
        # Загрузка конфигурации
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Инициализация менеджеров
        security = SecurityManager(config)
        db = DatabaseManager(config, security)
        generator = KeyGenerator(config, security, db)
        
        # Генерация ключей
        print("Генерация лицензионных ключей локально...")
        results = generator.generate_keys_for_all_types()
        
        # Вывод результатов
        print("\n✅ Ключи успешно сгенерированы!")
        print("\n📊 Результаты генерации:")
        
        total_generated = 0
        all_keys = {}
        
        for license_type, result in results.items():
            print(f"\n{license_type}:")
            print(f"  Успешно: {result['success_count']}/{result['total_attempted']}")
            print(f"  Ключи: {', '.join(result['keys'][:5])}")  # Показываем первые 5 ключей
            if len(result['keys']) > 5:
                print(f"  ... и еще {len(result['keys']) - 5}")
            
            total_generated += result['success_count']
            all_keys[license_type] = result['keys']
        
        print(f"\n🎉 Всего сгенерировано ключей: {total_generated}")
        
        # Сохранение ключей в файл
        output_file = 'generated_keys.json'
        with open(output_file, 'w') as f:
            json.dump(all_keys, f, indent=2)
        print(f"\n💾 Все ключи сохранены в: {output_file}")
        
        # Показать пример использования
        print(f"\n🔑 Примеры ключей с префиксами:")
        for license_type in all_keys.keys():
            if all_keys[license_type]:
                prefix = generator.prefixes.get(license_type, "")
                print(f"  {license_type}: {all_keys[license_type][0]} (начинается с '{prefix}')")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    generate_keys_locally()