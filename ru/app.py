# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import base64
import hmac
import hashlib
from database import DatabaseManager
from security import SecurityManager
from key_generator import KeyGenerator

class LicenseServer:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.security = SecurityManager(self.config)
        self.db = DatabaseManager(self.config, self.security)
        self.key_generator = KeyGenerator(self.config, self.security, self.db)
        self.app = self.create_flask_app()
    
    def load_config(self, config_path):
        """Загрузка конфигурации"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def setup_logging(self):
        """Настройка логирования"""
        logging_config = self.config['logging']
        
        handler = RotatingFileHandler(
            logging_config['file'],
            maxBytes=logging_config['max_file_size_mb'] * 1024 * 1024,
            backupCount=logging_config['backup_count']
        )
        
        logging.basicConfig(
            level=getattr(logging, logging_config['level']),
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[handler]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def create_flask_app(self):
        """Создание Flask приложения"""
        app = Flask(__name__)
        
        # Настройка ограничителя запросов с хранилищем
        limiter_config = self.config['rate_limiting']
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[f"{self.config['security']['max_requests_per_minute']} per minute"],
            storage_uri=limiter_config['storage_uri'],
            strategy=limiter_config['strategy'],
            storage_options=limiter_config['storage_options']
        )
        
        @app.before_request
        def before_request():
            """Проверка безопасности перед каждым запросом"""
            # Пропускаем health check
            if request.path == '/health':
                return
            
            if not self.authenticate_request():
                return jsonify({
                    'status': 'error',
                    'message': 'Аутентификация не удалась'
                }), 401
            
            if not self.check_ip_restrictions():
                return jsonify({
                    'status': 'error', 
                    'message': 'IP адрес не разрешен'
                }), 403
        
        @app.route('/api/validate', methods=['POST'])
        @self.limiter.limit(f"{self.config['security']['max_requests_per_minute']} per minute")
        def validate_license():
            """Эндпоинт для проверки лицензии"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'status': 'error',
                        'message': 'JSON данные не предоставлены'
                    }), 400
                
                required_fields = ['license_key', 'license_type', 'timestamp']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            'status': 'error',
                            'message': f'Отсутствует обязательное поле: {field}'
                        }), 400
                

                
                license_key = data['license_key']
                license_type = data['license_type']
                timestamp = data['timestamp']
                client_info = data.get('client_info', '')
                
                # Проверка формата ключа
                if len(license_key) != self.config['licensing']['key_length']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Неверный формат ключа'
                    }), 400
                
                # Проверка типа лицензии
                if license_type not in self.config['licensing']['license_types']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Неверный тип лицензии'
                    }), 400
                
                # Валидация лицензии
                is_valid, message = self.db.validate_license(
                    license_key,
                    license_type,
                    client_info,
                    get_remote_address()
                )
                
                response_data = {
                    'status': 'success' if is_valid else 'error',
                    'message': message,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Логирование запроса
                if self.config['logging']['log_requests']:
                    self.logger.info(
                        f"Проверка лицензии - Ключ: {license_key}, "
                        f"Тип: {license_type}, Валиден: {is_valid}, "
                        f"IP: {get_remote_address()}"
                    )
                
                return jsonify(response_data), 200 if is_valid else 403
                
            except Exception as e:
                self.logger.error(f"Ошибка в validate_license: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': 'Внутренняя ошибка сервера'
                }), 500
        
        @app.route('/api/admin/generate-keys', methods=['POST'])
        @self.limiter.limit(f"{self.config['security']['max_requests_per_minute']} per minute")
        def generate_keys():
            """Эндпоинт для генерации ключей (только для админов)"""
            try:
                auth_header = request.headers.get('Authorization')
                if not self.verify_admin_token(auth_header):
                    return jsonify({
                        'status': 'error',
                        'message': 'Требуется аутентификация администратора'
                    }), 401
                
                results = self.key_generator.generate_keys_for_all_types()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Ключи успешно сгенерированы',
                    'results': results
                }), 200
                
            except Exception as e:
                self.logger.error(f"Ошибка в generate_keys: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': 'Внутренняя ошибка сервера'
                }), 500
        
        @app.route('/api/admin/stats', methods=['GET'])
        @self.limiter.limit(f"{self.config['security']['max_requests_per_minute']} per minute")
        def get_stats():
            """Эндпоинт для получения статистики (только для админов)"""
            try:
                auth_header = request.headers.get('Authorization')
                if not self.verify_admin_token(auth_header):
                    return jsonify({
                        'status': 'error',
                        'message': 'Требуется аутентификация администратора'
                    }), 401
                
                stats = self.db.get_license_stats()
                
                return jsonify({
                    'status': 'success',
                    'stats': stats
                }), 200
                
            except Exception as e:
                self.logger.error(f"Ошибка в get_stats: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': 'Внутренняя ошибка сервера'
                }), 500
        
        @app.route('/health', methods=['GET'])
        def health_check():
            """Эндпоинт для проверки здоровья сервера"""
            return jsonify({
                'status': 'success',
                'message': 'Сервер работает',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        return app
    def _generate_hmac_signature(self, data: str) -> str:
        """Генерирует HMAC подпись на сервере"""
        try:
            secret_bytes = base64.b64decode(self.config['security']['hmac_secret'])
            signature = hmac.new(
                secret_bytes,
                data.encode('utf-8'),
                hashlib.sha256
            ).digest()
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"❌ Ошибка генерации HMAC на сервере: {e}")
            return ""
    def authenticate_request(self):
        """Аутентификация запроса"""
        if not self.config['security']['api_key_required']:
            return True
        
        api_key = request.headers.get('X-API-Key')
        if api_key not in self.config['security']['api_keys']:
            return False
        
        if self.config['security']['require_encrypted_communication']:
            signature = request.headers.get('X-Signature')
            if not signature:
                print("❌ HMAC подпись отсутствует")
                return False
            
            # Получаем данные запроса
            data = request.get_json()
            if not data:
                print("❌ Нет данных для проверки подписи")
                return False
            
            # Форматируем так же как клиент
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            print(f"🔐 Данные для проверки: {data_str}")
            print(f"🔐 Полученная подпись: {signature}")
            
            # Генерируем ожидаемую подпись
            expected_signature = self._generate_hmac_signature(data_str)
            print(f"🔐 Ожидаемая подпись: {expected_signature}")
            
            # Сравниваем подписи
            if not hmac.compare_digest(signature, expected_signature):
                print("❌ HMAC подписи не совпадают")
                return False
            
            print("✅ HMAC подпись верна")
        
        return True 
    
    def verify_admin_token(self, auth_header):
        """Проверка административного токена"""
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header[7:]
        payload = self.security.verify_jwt_token(token)
        return payload is not None and payload.get('admin') == True
    
    def check_ip_restrictions(self):
        """Проверка ограничений по IP"""
        client_ip = get_remote_address()
        allowed_ips = self.config['security']['allowed_ips']
        blocked_ips = self.config['security']['blocked_ips']
        
        if allowed_ips and client_ip not in allowed_ips:
            return False
        
        if blocked_ips and client_ip in blocked_ips:
            return False
        
        return True
    
    def run(self):
        """Запуск сервера"""
        server_config = self.config['server']
        
        if server_config['ssl_enabled']:
            ssl_context = (
                server_config['ssl_cert_path'],
                server_config['ssl_key_path']
            )
        else:
            ssl_context = None
        
        self.app.run(
            host=server_config['host'],
            port=server_config['port'],
            debug=server_config['debug'],
            ssl_context=ssl_context
        )