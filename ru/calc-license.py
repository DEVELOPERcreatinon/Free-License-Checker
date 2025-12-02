import urllib3
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
import time
import math
from math import *
import os
import pickle
import statistics
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import numpy as np
from scipy import integrate, optimize, special, stats, linalg
import sympy as sp
from sympy import symbols, solve, diff, integrate as sp_integrate
import decimal
from decimal import Decimal, getcontext
import warnings
import requests
import json
import hashlib
import uuid
import platform
import hmac
import hashlib
import base64
import json

# Отключаем SSL предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# ==================== ЛИЦЕНЗИОННАЯ СИСТЕМА ====================

class LicenseManager:
    """Менеджер лицензий для калькулятора с привязкой к устройству"""
    
    def __init__(self):
        self.license_server_url = "https://192.168.0.104:5000"
        self.license_key = None
        self.license_type = None
        self.license_valid = False
        self.device_id = self._generate_device_id()
        self.license_features = self._get_default_features()
        self.api_key = "Your-api-key"
        self.state_file = "calculator_state.pkl"
        self.verified_keys_file = "verified_keys.json"
        self.verified_keys = self._load_verified_keys()
        self.cert_path = "cert.pem"
        self.hmac_secret = "your-secret"
    def _generate_hmac_signature(self, data: dict) -> str:
        """Генерирует HMAC подпись для данных"""
        try:
            # Форматируем JSON ТОЧНО так же как на сервере
            # Сервер использует: json.dumps(data, sort_keys=True, separators=(',', ':'))
            payload_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            
            print(f"🔐 Данные для подписи: {payload_str}")
            
            # Декодируем base64 секрет
            secret_bytes = base64.b64decode(self.hmac_secret)
            
            # Создаем HMAC подпись
            signature = hmac.new(
                secret_bytes,
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            # Кодируем в base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            print(f"🔐 Сгенерированная подпись: {signature_b64}")
            
            return signature_b64
            
        except Exception as e:
            print(f"⚠️ Ошибка генерации HMAC: {e}")
            return ""
    def _load_verified_keys(self) -> Dict[str, Dict]:
        """Загрузка подтвержденных ключей из файла"""
        try:
            if os.path.exists(self.verified_keys_file):
                with open(self.verified_keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_verified_keys(self):
        """Сохранение подтвержденных ключей в файл"""
        try:
            with open(self.verified_keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.verified_keys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить verified_keys: {e}")
    
    def _generate_device_id(self) -> str:
        """Генерирует уникальный ID устройства"""
        try:
            # Комбинируем несколько идентификаторов для уникальности
            system_info = f"{platform.node()}-{platform.system()}-{platform.processor()}"
            # Добавляем MAC адрес если доступен
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,8*6,8)][::-1])
                system_info += f"-{mac}"
            except:
                pass
            
            # Создаем хеш
            device_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
            return device_id
        except Exception:
            # Fallback - случайный ID
            return str(uuid.uuid4())[:16]
        
    def _get_default_features(self) -> Dict[str, bool]:
        """Возвращает базовые функции (без лицензии)"""
        return {
            'basic_calculations': True,
            'trigonometry': True,
            'logarithms': True,
            'constants': True,
            'variables': True,
            'history': True,
            
            # Премиум функции (требуют лицензию)
            'high_precision': False,
            'physics_engine': False,
            'math_engine': False,
            'statistics_engine': False,
            'symbolic_math': False,
            'advanced_functions': False,
            'export_features': False,
            'custom_precision': False,
        }
    
    def _get_license_features(self, license_type: str) -> Dict[str, bool]:
        """Возвращает функции в зависимости от типа лицензии"""
        features = self._get_default_features()
        
        if license_type == "STUDENT":
            features.update({
                'high_precision': True,
                'physics_engine': True,
                'math_engine': True,
                'statistics_engine': True,
                'custom_precision': True,
            })
        elif license_type == "PRO":
            features.update({
                'high_precision': True,
                'physics_engine': True,
                'math_engine': True,
                'statistics_engine': True,
                'symbolic_math': True,
                'advanced_functions': True,
                'custom_precision': True,
            })
        elif license_type == "BUSINESS":
            features.update({
                'high_precision': True,
                'physics_engine': True,
                'math_engine': True,
                'statistics_engine': True,
                'symbolic_math': True,
                'advanced_functions': True,
                'export_features': True,
                'custom_precision': True,
            })
            
        return features
    
    def validate_license(self, license_key: str) -> Tuple[bool, str]:
        """Проверяет лицензию на сервере с привязкой к устройству"""
        try:
            print(f"🔐 Отправка запроса на сервер: {self.license_server_url}")
            
            license_type = self._detect_license_type(license_key)
            
            payload = {
                'license_key': license_key,
                'license_type': license_type,
                'timestamp': datetime.utcnow().isoformat(),
                'client_info': f'calculator_{self.device_id}',
                'device_id': self.device_id
            }
            
            # Генерируем HMAC подпись ДО отправки
            signature = self._generate_hmac_signature(payload)
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            print(f"📦 Отправляемые данные: {json.dumps(payload, indent=2)}")
            print(f"🔐 HMAC подпись: {signature}")
            print(f"📋 Заголовки: {headers}")
            
            response = requests.post(
                f"{self.license_server_url}/api/validate",
                json=payload,  # Отправляем оригинальный payload
                headers=headers,
                timeout=10,
                verify=False
            )
            
            print(f"📡 Статус ответа: {response.status_code}")
            print(f"📄 Тело ответа: {response.text}")
            print(f"📋 Заголовки ответа: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    self._add_verified_key(license_key, license_type)
                    self.license_key = license_key
                    self.license_type = license_type
                    self.license_valid = True
                    self.license_features = self._get_license_features(license_type)
                    self._auto_save()
                    return True, f"✅ Лицензия {license_type} активирована! Доступны премиум функции."
                else:
                    return False, f"❌ Ошибка лицензии: {data.get('message', 'Неизвестная ошибка')}"
            elif response.status_code == 401:
                return False, "❌ Ошибка аутентификации (401)"
            elif response.status_code == 403:
                return False, "❌ Доступ запрещен (403)"
            else:
                return False, f"❌ Ошибка сервера: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ Ошибка проверки лицензии: {str(e)}"

    def _validate_with_ssl_bypass(self, license_key: str) -> Tuple[bool, str]:
        """Проверка лицензии с отключенной SSL проверкой"""
        try:
            print("⚠️  Используется небезопасное соединение (самоподписанный сертификат)")
            
            license_type = self._detect_license_type(license_key)
            
            payload = {
                'license_key': license_key,
                'license_type': license_type,
                'timestamp': datetime.utcnow().isoformat(),
                'client_info': f'calculator_{self.device_id}',
                'device_id': self.device_id
            }
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.license_server_url}/api/validate",
                json=payload,
                headers=headers,
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    self._add_verified_key(license_key, license_type)
                    
                    self.license_key = license_key
                    self.license_type = license_type
                    self.license_valid = True
                    self.license_features = self._get_license_features(license_type)
                    self._auto_save()
                    
                    return True, f"✅ Лицензия {license_type} активирована! Доступны премиум функции."
                else:
                    return False, f"❌ Ошибка лицензии: {data.get('message', 'Неизвестная ошибка')}"
            else:
                return self._validate_license_offline(license_key)
                
        except Exception as e:
            return False, f"❌ Ошибка SSL соединения: {str(e)}"

    def _validate_with_certificate(self, license_key: str) -> Tuple[bool, str]:
        """Проверка лицензии с использованием сертификата"""
        try:
            license_type = self._detect_license_type(license_key)
            
            payload = {
                'license_key': license_key,
                'license_type': license_type,
                'timestamp': datetime.utcnow().isoformat(),
                'client_info': f'calculator_{self.device_id}',
                'device_id': self.device_id
            }
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Используем сертификат если он существует
            verify_cert = self.cert_path if os.path.exists(self.cert_path) else True
            
            response = requests.post(
                f"{self.license_server_url}/api/validate",
                json=payload,
                headers=headers,
                timeout=10,
                verify=verify_cert
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    self._add_verified_key(license_key, license_type)
                    
                    self.license_key = license_key
                    self.license_type = license_type
                    self.license_valid = True
                    self.license_features = self._get_license_features(license_type)
                    self._auto_save()
                    
                    return True, f"✅ Лицензия {license_type} активирована!"
                else:
                    return False, f"❌ Ошибка лицензии: {data.get('message', 'Неизвестная ошибка')}"
            else:
                return self._validate_license_offline(license_key)
                
        except requests.exceptions.SSLError:
            # Если SSL ошибка, пробуем без проверки
            return self._validate_with_ssl_bypass(license_key)
        except Exception as e:
            return False, f"❌ Ошибка соединения: {str(e)}"

    def _add_verified_key(self, license_key: str, license_type: str):
        """Добавляет ключ в список подтвержденных"""
        self.verified_keys[license_key] = {
            'type': license_type,
            'verified_at': datetime.now().isoformat(),
            'device_id': self.device_id
        }
        self._save_verified_keys()
    
    def _is_key_verified(self, license_key: str) -> bool:
        """Проверяет, был ли ключ подтвержден сервером"""
        return license_key in self.verified_keys
    
    def _detect_license_type(self, license_key: str) -> str:
        """Определяет тип лицензии по ключу"""
        license_key_upper = license_key.upper()
        
        if license_key_upper.startswith("BUS"):
            return "BUSINESS"
        elif license_key_upper.startswith("PRO"):
            return "PRO" 
        elif license_key_upper.startswith("STU"):
            return "STUDENT"
        else:
            return "STUDENT"
    
    def _validate_license_offline(self, license_key: str) -> Tuple[bool, str]:
        """Оффлайн проверка лицензии - ТОЛЬКО для подтвержденных ключей"""
        # Проверяем базовый формат
        if len(license_key) != 16:
            return False, "❌ Неверный формат лицензионного ключа"
        
        # Проверяем, был ли ключ подтвержден сервером
        if not self._is_key_verified(license_key):
            return False, "❌ Ключ не подтвержден сервером. Требуется онлайн-активация."
        
        # Получаем информацию о подтвержденном ключе
        key_info = self.verified_keys.get(license_key, {})
        license_type = key_info.get('type', self._detect_license_type(license_key))
        
        # Проверяем привязку к устройству
        saved_device_id = key_info.get('device_id')
        if saved_device_id and saved_device_id != self.device_id:
            return False, "❌ Лицензия привязана к другому устройству"
        
        self.license_key = license_key
        self.license_type = license_type
        self.license_valid = True
        self.license_features = self._get_license_features(license_type)
        
        # Автосохранение при оффлайн активации
        self._auto_save()
        
        return True, f"✅ Лицензия {license_type} активирована (оффлайн-режим)"
    
    def _auto_save(self):
        """Автосохранение состояния лицензии"""
        try:
            state = {
                'license_key': self.license_key,
                'license_type': self.license_type,
                'license_valid': self.license_valid,
                'license_features': self.license_features,
                'device_id': self.device_id,
                'timestamp': datetime.now().timestamp()
            }
            
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            print(f"⚠️ Не удалось автосохранить лицензию: {e}")
    
    def auto_load(self) -> bool:
        """Автозагрузка состояния лицензии"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)
                
                # Проверяем привязку к устройству
                saved_device_id = state.get('device_id')
                if saved_device_id != self.device_id:
                    print("⚠️ Лицензия привязана к другому устройству")
                    return False
                
                # Восстанавливаем лицензию
                self.license_key = state.get('license_key')
                self.license_type = state.get('license_type')
                self.license_valid = state.get('license_valid', False)
                self.license_features = state.get('license_features', self._get_default_features())
                
                # Проверяем, что ключ все еще подтвержден
                if self.license_valid and self.license_key and not self._is_key_verified(self.license_key):
                    print("⚠️ Лицензия больше не подтверждена")
                    self.license_valid = False
                    return False
                
                if self.license_valid:
                    print(f"🔑 Лицензия {self.license_type} автоматически восстановлена")
                    return True
                    
        except Exception as e:
            print(f"⚠️ Не удалось автозагрузить лицензию: {e}")
        
        return False
    
    def has_feature(self, feature: str) -> bool:
        """Проверяет доступность функции"""
        return self.license_features.get(feature, False)
    
    def get_license_info(self) -> Dict[str, Any]:
        """Возвращает информацию о лицензии"""
        verification_status = "✅ Подтвержден" if self._is_key_verified(self.license_key) else "❌ Не подтвержден" if self.license_key else "N/A"
        
        return {
            'valid': self.license_valid,
            'type': self.license_type,
            'key': self.license_key,
            'features': self.license_features,
            'device_id': self.device_id,
            'verified': verification_status
        }
    
    def reset_license(self):
        """Сбрасывает лицензию"""
        self.license_key = None
        self.license_type = None
        self.license_valid = False
        self.license_features = self._get_default_features()
        
        # Удаляем файл состояния
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
        except:
            pass

# ==================== КЛАССЫ ИСКЛЮЧЕНИЙ ====================

class CalculatorError(Exception):
    """Базовое исключение калькулятора"""
    pass

class CalculationError(CalculatorError):
    """Ошибка вычисления выражения"""
    pass

class PhysicsError(CalculatorError):
    """Ошибка в физических расчетах"""
    pass

class MathError(CalculatorError):
    """Ошибка в математических операциях"""
    pass

class StatisticsError(CalculatorError):
    """Ошибка в статистических расчетах"""
    pass

class LicenseError(CalculatorError):
    """Ошибка лицензии"""
    pass

# ==================== БЕЗОПАСНЫЙ ВЫЧИСЛИТЕЛЬ ====================

class ExpressionParser:
    """Безопасный парсер математических выражений"""
    
    @staticmethod
    def tokenize(expression: str) -> List[str]:
        """Разбивает выражение на токены"""
        expression = expression.replace(' ', '')
        tokens = []
        current_token = ''
        
        for char in expression:
            if char.isalnum() or char == '.':
                current_token += char
            else:
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                if char != ' ':
                    tokens.append(char)
        
        if current_token:
            tokens.append(current_token)
            
        return tokens
    
    @staticmethod
    def is_valid_expression(tokens: List[str]) -> bool:
        """Проверяет безопасность выражения"""
        valid_chars = set('+-*/^().0123456789abcdefghijklmnopqrstuvwxyz_')
        for token in tokens:
            if not all(c in valid_chars for c in token.lower()):
                return False
        return True

class SafeEvaluator:
    """Безопасный вычислитель выражений"""
    
    def __init__(self, license_manager: LicenseManager):
        self.license_manager = license_manager
        self.functions = self._init_functions()
        self.constants = self._init_constants()
    
    def _init_functions(self) -> Dict[str, Any]:
        """Инициализация безопасных функций"""
        functions = {
            # Тригонометрия
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'atan2': math.atan2,
            
            # Экспоненты и логарифмы
            'exp': math.exp, 'log': math.log, 'log10': math.log10, 
            'log2': math.log2, 'sqrt': math.sqrt, 'pow': math.pow,
            
            # Округление
            'ceil': math.ceil, 'floor': math.floor, 'round': round,
            'abs': abs,
        }
        
        # Расширенные функции требуют лицензии
        if self.license_manager.has_feature('advanced_functions'):
            functions.update({
                'gamma': math.gamma, 'lgamma': math.lgamma, 
                'factorial': math.factorial, 'erf': math.erf,
            })
            
        return functions
    
    def _init_constants(self) -> Dict[str, float]:
        """Инициализация констант"""
        return {
            'pi': math.pi, 'e': math.e, 'tau': math.tau,
            'inf': float('inf'), 'nan': float('nan'),
        }
    
    def evaluate(self, expression: str, variables: Dict[str, float] = None, 
                high_precision: bool = False) -> float:
        """Безопасное вычисление выражения"""
        # Проверка лицензии для высокоточной арифметики
        if high_precision and not self.license_manager.has_feature('high_precision'):
            raise LicenseError("Высокая точность требует активации лицензии")
            
        try:
            # Предобработка
            expr = self._preprocess_expression(expression)
            
            # Проверка безопасности
            tokens = ExpressionParser.tokenize(expr)
            if not ExpressionParser.is_valid_expression(tokens):
                raise CalculationError("Выражение содержит недопустимые символы")
            
            # Создание окружения
            env = {**self.constants, **self.functions}
            if variables:
                env.update(variables)
            
            # Компиляция и выполнение
            code = compile(expr, '<string>', 'eval')
            result = eval(code, {'__builtins__': {}}, env)
            
            if not isinstance(result, (int, float)):
                raise CalculationError("Результат должен быть числом")
            
            # Высокая точность через decimal
            if high_precision:
                if not self.license_manager.has_feature('high_precision'):
                    raise LicenseError("Высокая точность требует лицензии PRO или BUSINESS")
                    
                with decimal.localcontext() as ctx:
                    ctx.prec = 1000  # Очень высокая точность для вычислений
                    decimal_result = Decimal(str(result))
                    return float(decimal_result)
            else:
                return float(result)
            
        except SyntaxError as e:
            raise CalculationError(f"Синтаксическая ошибка: {e}")
        except NameError as e:
            raise CalculationError(f"Неизвестная переменная или функция: {e}")
        except ZeroDivisionError:
            raise CalculationError("Деление на ноль")
        except OverflowError:
            raise CalculationError("Переполнение вычислений")
        except Exception as e:
            raise CalculationError(f"Ошибка вычисления: {e}")

    def _preprocess_expression(self, expr: str) -> str:
        """Предобработка выражения"""
        expr = expr.replace('^', '**')
        expr = expr.replace('π', 'pi')
        return expr

# ==================== КАЛЬКУЛЯТОР ====================

@dataclass
class CalculationResult:
    """Результат вычисления"""
    expression: str
    result: float
    timestamp: float
    success: bool = True
    error_message: str = ""

class ScientificCalculator:
    """Научный калькулятор с историей и переменными"""
    
    def __init__(self, license_manager: LicenseManager, precision: int = 10, angle_mode: str = 'rad'):
        self.license_manager = license_manager
        self.precision = precision
        self.angle_mode = angle_mode
        self.evaluator = SafeEvaluator(license_manager)
        self.variables: Dict[str, float] = {}
        self.history: List[CalculationResult] = []
        self.history_file = "calculator_history.pkl"
        self._init_default_variables()
        self._load_history()
    
    def _init_default_variables(self):
        """Инициализация физических констант"""
        physical_constants = {
            'G': 6.67430e-11,
            'c': 299792458,
            'g': 9.80665,
            'h': 6.62607015e-34,
            'k': 1.380649e-23,
            'R': 8.314462618,
            'Na': 6.02214076e23,
            'e_charge': 1.602176634e-19,
        }
        self.variables.update(physical_constants)
    
    def _save_history(self):
        """Сохранение истории в файл"""
        try:
            with open(self.history_file, 'wb') as f:
                pickle.dump(self.history, f)
        except Exception as e:
            print(f"⚠️ Предупреждение: не удалось сохранить историю: {e}")
    
    def _load_history(self):
        """Загрузка истории из файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'rb') as f:
                    self.history = pickle.load(f)
                print(f"📖 Загружено {len(self.history)} записей из истории")
        except Exception as e:
            print(f"⚠️ Предупреждение: не удалось загрузить историю: {e}")
            self.history = []
    
    def calculate(self, expression: str) -> float:
        """Вычисление выражения с сохранением в историю"""
        try:
            # Проверка лицензии для расширенных функций
            if any(func in expression.upper() for func in ['GAMMA', 'LGAMMA', 'ERF']):
                if not self.license_manager.has_feature('advanced_functions'):
                    raise LicenseError("Расширенные математические функции требуют лицензии PRO или BUSINESS")
            
            # Временная замена переменных
            temp_vars = self.variables.copy()
            
            # Конвертация углов для тригонометрических функций
            if self.angle_mode != 'rad':
                temp_vars.update(self._get_angle_conversion_functions())
            
            # Используем высокую точность если нужно
            high_precision = self.precision > 15
            result = self.evaluator.evaluate(expression, temp_vars, high_precision)
            
            # Округление с учетом высокой точности
            if self.precision > 15:
                if not self.license_manager.has_feature('high_precision'):
                    raise LicenseError("Высокая точность (>15 знаков) требует лицензии")
                    
                with decimal.localcontext() as ctx:
                    ctx.prec = self.precision + 10
                    decimal_result = Decimal(str(result))
                    rounded_result = float(round(decimal_result, self.precision))
            else:
                rounded_result = round(result, self.precision)
            
            # Сохранение в историю
            calc_result = CalculationResult(
                expression=expression,
                result=rounded_result,
                timestamp=time.time()
            )
            self.history.append(calc_result)
            
            # Автосохранение истории
            if len(self.history) % 10 == 0:
                self._save_history()
            
            return rounded_result
            
        except (CalculationError, LicenseError) as e:
            # Сохранение ошибки в историю
            error_result = CalculationResult(
                expression=expression,
                result=float('nan'),
                timestamp=time.time(),
                success=False,
                error_message=str(e)
            )
            self.history.append(error_result)
            self._save_history()
            raise
    
    def _get_angle_conversion_functions(self) -> Dict[str, Any]:
        """Получение функций с конвертацией углов"""
        if self.angle_mode == 'deg':
            return {
                'sin': lambda x: math.sin(math.radians(x)),
                'cos': lambda x: math.cos(math.radians(x)),
                'tan': lambda x: math.tan(math.radians(x)),
                'asin': lambda x: math.degrees(math.asin(x)),
                'acos': lambda x: math.degrees(math.acos(x)),
                'atan': lambda x: math.degrees(math.atan(x)),
            }
        elif self.angle_mode == 'grad':
            return {
                'sin': lambda x: math.sin(x * math.pi / 200),
                'cos': lambda x: math.cos(x * math.pi / 200),
                'tan': lambda x: math.tan(x * math.pi / 200),
                'asin': lambda x: x * 200 / math.pi,
                'acos': lambda x: x * 200 / math.pi,
                'atan': lambda x: x * 200 / math.pi,
            }
        return {}
    
    def set_variable(self, name: str, value: float):
        """Установка переменной"""
        if not name.isidentifier():
            raise CalculationError(f"Недопустимое имя переменной: {name}")
        self.variables[name] = value
    
    def get_history(self, limit: int = 10) -> List[CalculationResult]:
        """Получение истории вычислений"""
        return self.history[-limit:] if limit else self.history
    
    def clear_history(self):
        """Очистка истории"""
        self.history.clear()
        self._save_history()
    
    def export_history(self, filename: str = "calculator_history_export.txt"):
        """Экспорт истории в текстовый файл"""
        if not self.license_manager.has_feature('export_features'):
            raise LicenseError("Экспорт истории требует лицензии BUSINESS")
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ИСТОРИЯ ВЫЧИСЛЕНИЙ\n")
                f.write("=" * 50 + "\n")
                for i, result in enumerate(self.history):
                    status = "УСПЕХ" if result.success else "ОШИБКА"
                    f.write(f"{i+1:4d}. [{status}] {result.expression}\n")
                    if result.success:
                        if self.precision > 15:
                            f.write(f"     Результат: {result.result:.15f}...\n")
                        else:
                            f.write(f"     Результат: {result.result}\n")
                    else:
                        f.write(f"     Ошибка: {result.error_message}\n")
                    time_str = datetime.fromtimestamp(result.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"     Время: {time_str}\n")
                    f.write("-" * 50 + "\n")
            print(f"✅ История экспортирована в {filename}")
        except Exception as e:
            print(f"❌ Ошибка экспорта истории: {e}")
    
    def format_result(self, result: float) -> str:
        """Форматирует результат с учетом текущей точности"""
        if self.precision > 15:
            display_precision = min(self.precision, 50)
            return f"{result:.{display_precision}f}"
        else:
            return f"{result}"

# ==================== ФИЗИЧЕСКИЙ ДВИГАТЕЛЬ ====================

class PhysicsEngine:
    """Двигатель физических расчетов"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Проверяет наличие лицензии для физических расчетов"""
        if not self.license_manager.has_feature('physics_engine'):
            raise LicenseError("Физические расчеты требуют активации лицензии")
    
    def pendulum_period(self, length: float, gravity: float = None) -> float:
        """Период математического маятника"""
        self._check_license()
        
        if length <= 0:
            raise PhysicsError("Длина маятника должна быть положительной")
        
        if gravity is None:
            gravity = self.calc.variables.get('g', 9.80665)
        
        if gravity <= 0:
            raise PhysicsError("Ускорение свободного падения должно быть положительным")
        
        return 2 * math.pi * math.sqrt(length / gravity)
    
    def lorentz_factor(self, velocity: float) -> float:
        """Релятивистский γ-фактор"""
        self._check_license()
        
        c = self.calc.variables.get('c', 299792458)
        
        if abs(velocity) >= c:
            raise PhysicsError("Скорость не может превышать скорость света")
        
        return 1 / math.sqrt(1 - (velocity / c) ** 2)
    
    def kinetic_energy(self, mass: float, velocity: float) -> float:
        """Кинетическая энергия"""
        self._check_license()
        
        if mass < 0:
            raise PhysicsError("Масса не может быть отрицательной")
        
        return 0.5 * mass * velocity ** 2
    
    def schwarzschild_radius(self, mass: float) -> float:
        """Радиус Шварцшильда"""
        self._check_license()
        
        if mass <= 0:
            raise PhysicsError("Масса должна быть положительной")
        
        G = self.calc.variables.get('G', 6.67430e-11)
        c = self.calc.variables.get('c', 299792458)
        
        return 2 * G * mass / (c ** 2)
    
    def orbital_velocity(self, mass: float, radius: float) -> float:
        """Первая космическая скорость"""
        self._check_license()
        
        if mass <= 0 or radius <= 0:
            raise PhysicsError("Масса и радиус должны быть положительными")
        
        G = self.calc.variables.get('G', 6.67430e-11)
        return math.sqrt(G * mass / radius)
    
    def escape_velocity(self, mass: float, radius: float) -> float:
        """Вторая космическая скорость"""
        self._check_license()
        
        if mass <= 0 or radius <= 0:
            raise PhysicsError("Масса и радиус должны быть положительными")
        
        return math.sqrt(2) * self.orbital_velocity(mass, radius)

# ==================== МАТЕМАТИЧЕСКИЙ ДВИГАТЕЛЬ ====================

class MathEngine:
    """Двигатель математических расчетов"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Проверяет наличие лицензии для математических расчетов"""
        if not self.license_manager.has_feature('math_engine'):
            raise LicenseError("Математические расчеты требуют активации лицензии")
    
    def solve_equation(self, equation: str, variable: str = 'x') -> List[float]:
        """Решение алгебраического уравнения"""
        self._check_license()
        
        try:
            var = symbols(variable)
            
            if '=' in equation:
                parts = equation.split('=')
                if len(parts) == 2:
                    left, right = parts
                    expr = sp.sympify(f"({left}) - ({right})")
                else:
                    raise MathError("Неверный формат уравнения")
            else:
                expr = sp.sympify(equation)
            
            solutions = solve(expr, var)
            
            numeric_solutions = []
            for sol in solutions:
                try:
                    numeric_val = float(sol.evalf())
                    numeric_solutions.append(numeric_val)
                except (TypeError, ValueError):
                    continue
            
            return numeric_solutions
            
        except Exception as e:
            raise MathError(f"Ошибка решения уравнения: {e}")
    
    def derivative(self, expression: str, variable: str = 'x', point: float = None) -> Union[str, float]:
        """Вычисление производной"""
        self._check_license()
        
        try:
            var = symbols(variable)
            expr = sp.sympify(expression)
            deriv = diff(expr, var)
            
            if point is not None:
                return float(deriv.subs(var, point).evalf())
            else:
                return str(deriv)
            
        except Exception as e:
            raise MathError(f"Ошибка вычисления производной: {e}")
    
    def definite_integral(self, expression: str, variable: str = 'x', 
                         limits: Tuple[float, float] = None) -> float:
        """Вычисление определенного интеграла"""
        self._check_license()
        
        if limits is None:
            raise MathError("Не указаны пределы интегрирования")
        
        try:
            a, b = limits
            var = symbols(variable)
            expr = sp.sympify(expression)
            
            result = sp_integrate(expr, (var, a, b))
            return float(result.evalf())
            
        except Exception as e:
            raise MathError(f"Ошибка вычисления интеграла: {e}")

# ==================== СТАТИСТИЧЕСКИЙ ДВИГАТЕЛЬ ====================

class StatisticsEngine:
    """Двигатель статистических расчетов"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Проверяет наличие лицензии для статистических расчетов"""
        if not self.license_manager.has_feature('statistics_engine'):
            raise LicenseError("Статистические расчеты требуют активации лицензии")
    
    def validate_data(self, data: List[float]) -> None:
        """Валидация входных данных"""
        if not data:
            raise StatisticsError("Данные не могут быть пустыми")
        
        if len(data) < 2:
            raise StatisticsError("Недостаточно данных для статистического анализа")
        
        if any(math.isnan(x) or math.isinf(x) for x in data):
            raise StatisticsError("Данные содержат NaN или бесконечности")
    
    def descriptive_statistics(self, data: List[float]) -> Dict[str, float]:
        """Описательная статистика"""
        self._check_license()
        self.validate_data(data)
        
        try:
            np_data = np.array(data)
            
            stats_dict = {
                'count': len(data),
                'mean': float(np.mean(np_data)),
                'median': float(np.median(np_data)),
                'std_dev': float(np.std(np_data, ddof=1)),
                'variance': float(np.var(np_data, ddof=1)),
                'min': float(np.min(np_data)),
                'max': float(np.max(np_data)),
                'range': float(np.ptp(np_data)),
                'q1': float(np.percentile(np_data, 25)),
                'q3': float(np.percentile(np_data, 75)),
                'iqr': float(np.percentile(np_data, 75) - np.percentile(np_data, 25)),
            }
            
            if len(data) > 2:
                try:
                    stats_dict['skewness'] = float(stats.skew(np_data))
                    stats_dict['kurtosis'] = float(stats.kurtosis(np_data))
                except:
                    stats_dict['skewness'] = float('nan')
                    stats_dict['kurtosis'] = float('nan')
            
            return stats_dict
        except Exception as e:
            raise StatisticsError(f"Ошибка вычисления статистики: {e}")
    
    def linear_regression(self, x_data: List[float], y_data: List[float]) -> Dict[str, float]:
        """Линейная регрессия"""
        self._check_license()
        
        if len(x_data) != len(y_data):
            raise StatisticsError("Размеры массивов x и y должны совпадать")
        
        self.validate_data(x_data)
        self.validate_data(y_data)
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
            
            return {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'std_error': std_err,
            }
        except Exception as e:
            raise StatisticsError(f"Ошибка линейной регрессии: {e}")

# ==================== Vim-СТИЛЬ ИНТЕРФЕЙС ====================

class VimStyleCalculator:
    """Калькулятор с Vim-подобным интерфейсом"""
    
    def __init__(self):
        self.license_manager = LicenseManager()
        self.calc = ScientificCalculator(self.license_manager)
        self.physics = PhysicsEngine(self.calc, self.license_manager)
        self.math = MathEngine(self.calc, self.license_manager)
        self.stats = StatisticsEngine(self.calc, self.license_manager)
        
        self.mode = "NORMAL"
        self.command_history: List[str] = []
        self.history_index = -1
        
        # Регистрация команд
        self.commands = self._register_commands()
    
    def _register_commands(self) -> Dict[str, Any]:
        """Регистрация всех доступных команд"""
        return {
            # Базовые команды
            ':q': self._cmd_quit,
            ':quit': self._cmd_quit,
            ':exit': self._cmd_quit,
            ':h': self._cmd_help,
            ':help': self._cmd_help,
            ':m': self._cmd_mode,
            ':clear': self._cmd_clear,
            ':history': self._cmd_history,
            ':precision': self._cmd_precision,
            ':angle': self._cmd_angle,
            
            # Лицензия
            ':license': self._cmd_license,
            ':activate': self._cmd_activate,
            ':license_info': self._cmd_license_info,
            
            # Переменные
            ':vars': self._cmd_vars,
            ':let': self._cmd_let,
            ':del': self._cmd_del,
            
            # Физика
            ':pendulum': self._cmd_pendulum,
            ':lorentz': self._cmd_lorentz,
            ':kinetic': self._cmd_kinetic,
            ':schwarzschild': self._cmd_schwarzschild,
            ':orbital': self._cmd_orbital,
            ':escape': self._cmd_escape,
            
            # Математика
            ':solve': self._cmd_solve,
            ':deriv': self._cmd_derivative,
            ':integral': self._cmd_integral,
            
            # Статистика
            ':stats': self._cmd_stats,
            ':regression': self._cmd_regression,
            
            # Система
            ':save': self._cmd_save,
            ':load': self._cmd_load,
            ':reset': self._cmd_reset,
            ':export_history': self._cmd_export_history,
        }
    
    def print_banner(self):
        """Печать баннера"""
        license_info = self.license_manager.get_license_info()
        license_status = "✅ АКТИВИРОВАНА" if license_info['valid'] else "❌ ОТСУТСТВУЕТ"
        license_type = license_info['type'] or "DEMO"
        
        precision_warning = ""
        if self.calc.precision > 50:
            precision_warning = " ⚠️ ВЫСОКАЯ ТОЧНОСТЬ"
        elif self.calc.precision > 15:
            precision_warning = " ⚠️"
        
        banner = f"""
╔════════════════════════════════════════════════════════════════╗
║                   VIM SCIENTIFIC CALCULATOR                    ║
║                        РЕЖИМ: {self.mode:<8}                         ║
║                   ЛИЦЕНЗИЯ: {license_type:<9} {license_status:<18} ║
║                   ТОЧНОСТЬ: {self.calc.precision} знаков{precision_warning:<18}        ║
║                   УГЛЫ: {self.calc.angle_mode:<4}                                   ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_help(self):
        """Показать справку"""
        license_info = self.license_manager.get_license_info()
        
        help_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                       КОМАНДЫ КАЛЬКУЛЯТОРА                     ║
║                    ЛИЦЕНЗИЯ: {license_info['type'] or 'DEMO':<10}                          ║
╚════════════════════════════════════════════════════════════════╗

🎯 ОСНОВНЫЕ КОМАНДЫ:
  :q, :quit, :exit           - Выход
  :h, :help                  - Справка
  :m normal|insert        - Смена режима
  :clear                     - Очистка экрана
  :history [N]               - История вычислений
  :precision N               - Установка точности (1-1000)
  :angle rad|deg|grad        - Режим углов

🔑 ЛИЦЕНЗИОННЫЕ КОМАНДЫ:
  :license                   - Информация о лицензии
  :activate КЛЮЧ            - Активировать лицензию
  :license_info              - Подробная информация

📊 ПЕРЕМЕННЫЕ:
  :vars                      - Показать переменные
  :let var = выражение        - Установить переменную
  :del var                   - Удалить переменную

🚀 ФИЗИЧЕСКИЕ КОМАНДЫ: {'✅' if license_info['features']['physics_engine'] else '❌'}
  :pendulum L [g]            - Период маятника
  :lorentz v                 - Релятивистский γ-фактор
  :kinetic m v               - Кинетическая энергия
  :schwarzschild M           - Радиус Шварцшильда
  :orbital M r               - Орбитальная скорость
  :escape M r                - Вторая космическая скорость

🧮 МАТЕМАТИЧЕСКИЕ КОМАНДЫ: {'✅' if license_info['features']['math_engine'] else '❌'}
  :solve уравнение [var]     - Решить уравнение
  :deriv выражение [var] [x] - Производная
  :integral выражение a b    - Определенный интеграл

📈 СТАТИСТИЧЕСКИЕ КОМАНДЫ: {'✅' if license_info['features']['statistics_engine'] else '❌'}
  :stats данные              - Описательная статистика
  :regression x_data y_data  - Линейная регрессия

💾 СИСТЕМНЫЕ КОМАНДЫ:
  :save [файл]               - Сохранить состояние
  :load [файл]               - Загрузить состояние
  :reset                     - Сброс калькулятора
  :export_history [файл]     - Экспорт истории в файл {'✅' if license_info['features']['export_features'] else '❌'}

📝 ПРИМЕРЫ:
  :m insert
  2 + 3 * sin(pi/4)
  :let r = 6371e3
  :activate YOUR_LICENSE_KEY
  :pendulum 1
  :stats [1,2,3,4,5]
  :solve x**2 - 4 = 0

💡 ДОСТУПНЫЕ ЛИЦЕНЗИИ:
  🎓 STUDENT  - Базовые научные функции
  ⚡ PRO      - Расширенные математические функции  
  🏢 BUSINESS - Полный функционал + экспорт
        """
        print(help_text)
    
    def _is_float(self, value: str) -> bool:
        """Проверяет, можно ли преобразовать строку в float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    # ==================== РЕАЛИЗАЦИИ КОМАНД ====================
    
    def _cmd_quit(self, args: List[str]) -> bool:
        """Команда выхода"""
        print("👋 До свидания!")
        self.calc._save_history()
        return False
    
    def _cmd_help(self, args: List[str]) -> bool:
        """Команда справки"""
        self.show_help()
        return True
    
    def _cmd_mode(self, args: List[str]) -> bool:
        """Смена режима"""
        if len(args) >= 1:
            mode = args[0].upper()
            if mode in ['NORMAL', 'INSERT']:
                self.mode = mode
                print(f"✅ Режим изменен на: {mode}")
            else:
                print("❌ Ошибка: доступные режимы - normal, insert")
        else:
            print("❌ Использование: :mode normal|insert")
        return True
    
    def _cmd_clear(self, args: List[str]) -> bool:
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    
    def _cmd_history(self, args: List[str]) -> bool:
        """История вычислений"""
        try:
            limit = int(args[0]) if args else 10
            history = self.calc.get_history(limit)
            
            print(f"\n📜 ИСТОРИЯ ВЫЧИСЛЕНИЙ (последние {len(history)} из {len(self.calc.history)}):")
            for i, result in enumerate(history):
                status = "✅" if result.success else "❌"
                if result.success:
                    formatted_result = self.calc.format_result(result.result)
                    print(f"  {i+1:2d}. {status} {result.expression} = {formatted_result}")
                else:
                    print(f"  {i+1:2d}. {status} {result.expression} -> ОШИБКА: {result.error_message}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_precision(self, args: List[str]) -> bool:
        """Установка точности"""
        if len(args) >= 1:
            try:
                precision = int(args[0])
                if 1 <= precision <= 1000:
                    if precision > 15 and not self.license_manager.has_feature('custom_precision'):
                        print("❌ Ошибка: высокая точность требует активации лицензии")
                        print("💡 Доступные лицензии: STUDENT, PRO, BUSINESS")
                        return True
                    
                    if precision > 50:
                        print("⚠️  ВНИМАНИЕ: Установлена высокая точность!")
                        print("   Это может замедлить вычисления и занять много памяти")
                        confirm = input("   Продолжить? (y/N): ")
                        if confirm.lower() != 'y':
                            print("❌ Установка точности отменена")
                            return True
                    
                    if precision > 100:
                        print(f"⚠️  Установлена ОЧЕНЬ высокая точность: {precision} знаков")
                        print("   Вычисления могут быть медленными")
                    
                    old_precision = self.calc.precision
                    self.calc.precision = precision
                    print(f"✅ Точность изменена: {old_precision} -> {precision} знаков")
                    
                    if precision > 15:
                        print("💡 Для просмотра полного результата используйте :history")
                        print("💡 Вычисления теперь используют высокоточную арифметику")
                else:
                    print("❌ Ошибка: точность должна быть от 1 до 1000")
            except ValueError:
                print("❌ Ошибка: точность должна быть целым числом")
        else:
            print("❌ Использование: :precision число")
        return True
    
    def _cmd_angle(self, args: List[str]) -> bool:
        """Установка режима углов"""
        if len(args) >= 1:
            mode = args[0].lower()
            if mode in ['rad', 'deg', 'grad']:
                self.calc.angle_mode = mode
                print(f"✅ Режим углов установлен: {mode}")
            else:
                print("❌ Ошибка: доступные режимы - rad, deg, grad")
        else:
            print("❌ Использование: :angle rad|deg|grad")
        return True
    
    def _cmd_license(self, args: List[str]) -> bool:
        """Информация о лицензии"""
        license_info = self.license_manager.get_license_info()
        
        print("\n🔑 ИНФОРМАЦИЯ О ЛИЦЕНЗИИ:")
        print(f"  Статус: {'✅ АКТИВИРОВАНА' if license_info['valid'] else '❌ ОТСУТСТВУЕТ'}")
        print(f"  Тип: {license_info['type'] or 'DEMO'}")
        print(f"  Ключ: {license_info['key'] or 'Не активирован'}")
        
        print("\n📋 ДОСТУПНЫЕ ФУНКЦИИ:")
        features = license_info['features']
        for feature, enabled in features.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {self._get_feature_description(feature)}")
        
        if not license_info['valid']:
            print("\n💡 Для активации введите: :activate ВАШ_ЛИЦЕНЗИОННЫЙ_КЛЮЧ")
            print("🎓 STUDENT - Базовые научные функции")
            print("⚡ PRO     - Расширенные математические функции")  
            print("🏢 BUSINESS - Полный функционал + экспорт")
        
        return True
    
    def _cmd_activate(self, args: List[str]) -> bool:
        """Активация лицензии"""
        if len(args) >= 1:
            license_key = args[0]
            success, message = self.license_manager.validate_license(license_key)
            
            print(message)
            
            if success:
                self.calc = ScientificCalculator(self.license_manager, self.calc.precision, self.calc.angle_mode)
                self.physics = PhysicsEngine(self.calc, self.license_manager)
                self.math = MathEngine(self.calc, self.license_manager)
                self.stats = StatisticsEngine(self.calc, self.license_manager)
                
                print("🎉 Поздравляем! Премиум функции теперь доступны!")
                self._cmd_license([])
        else:
            print("❌ Использование: :activate ЛИЦЕНЗИОННЫЙ_КЛЮЧ")
            print("💡 Пример: :activate BUS123456789ABCDE")
        
        return True
    
    def _cmd_license_info(self, args: List[str]) -> bool:
        """Подробная информация о лицензии"""
        license_info = self.license_manager.get_license_info()
        
        print("\n🔑 ПОДРОБНАЯ ИНФОРМАЦИЯ О ЛИЦЕНЗИИ:")
        print(f"  Статус: {'✅ АКТИВИРОВАНА' if license_info['valid'] else '❌ ОТСУТСТВУЕТ'}")
        print(f"  Тип: {license_info['type'] or 'DEMO'}")
        print(f"  Ключ: {license_info['key'] or 'Не активирован'}")
        
        print("\n🎯 УРОВНИ ЛИЦЕНЗИЙ:")
        print("  🎓 STUDENT  - Базовые научные функции")
        print("     • Вычисления с обычной точностью")
        print("     • Физические расчеты") 
        print("     • Статистические функции")
        print("     • Решение уравнений")
        
        print("\n  ⚡ PRO      - Расширенные возможности")
        print("     • Всё из STUDENT +")
        print("     • Высокая точность (до 1000 знаков)")
        print("     • Символьные вычисления")
        print("     • Расширенные математические функции")
        
        print("\n  🏢 BUSINESS - Профессиональный уровень")
        print("     • Всё из PRO +")
        print("     • Экспорт истории и данных")
        print("     • Приоритетная поддержка")
        
        return True
    
    def _get_feature_description(self, feature: str) -> str:
        """Возвращает описание функции"""
        descriptions = {
            'basic_calculations': 'Базовые вычисления',
            'trigonometry': 'Тригонометрические функции',
            'logarithms': 'Логарифмы и экспоненты',
            'constants': 'Математические константы',
            'variables': 'Работа с переменными',
            'history': 'История вычислений',
            'high_precision': 'Высокая точность (>15 знаков)',
            'physics_engine': 'Физические расчеты',
            'math_engine': 'Математические движки',
            'statistics_engine': 'Статистические расчеты',
            'symbolic_math': 'Символьные вычисления',
            'advanced_functions': 'Расширенные функции',
            'export_features': 'Экспорт данных',
            'custom_precision': 'Настройка точности',
        }
        return descriptions.get(feature, feature)
    
    def _cmd_vars(self, args: List[str]) -> bool:
        """Показать переменные"""
        print("\n📊 ПЕРЕМЕННЫЕ:")
        for var, val in self.calc.variables.items():
            print(f"  {var} = {val}")
        
        if not self.calc.variables:
            print("  (нет пользовательских переменных)")
        return True
    
    def _cmd_let(self, args: List[str]) -> bool:
        """Установка переменной"""
        try:
            if len(args) >= 3 and args[1] == '=':
                var_name = args[0]
                expr = ' '.join(args[2:])
                
                result = self.calc.calculate(expr)
                self.calc.set_variable(var_name, result)
                formatted_result = self.calc.format_result(result)
                print(f"✅ Установлено: {var_name} = {formatted_result}")
            else:
                print("❌ Использование: :let переменная = выражение")
                
        except (CalculatorError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_del(self, args: List[str]) -> bool:
        """Удаление переменной"""
        if len(args) >= 1:
            var_name = args[0]
            if var_name in self.calc.variables:
                del self.calc.variables[var_name]
                print(f"✅ Удалена переменная: {var_name}")
            else:
                print(f"❌ Ошибка: переменная '{var_name}' не найдена")
        else:
            print("❌ Использование: :del имя_переменной")
        return True
    
    def _cmd_pendulum(self, args: List[str]) -> bool:
        """Период маятника"""
        try:
            if len(args) >= 1:
                length = float(self.calc.calculate(args[0]))
                gravity = float(self.calc.calculate(args[1])) if len(args) > 1 else None
                
                period = self.physics.pendulum_period(length, gravity)
                print(f"✅ Период маятника: T = 2π√({length}/{gravity or 'g'}) = {period:.6f} с")
            else:
                print("❌ Использование: :pendulum длина [ускорение_свободного_падения]")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_lorentz(self, args: List[str]) -> bool:
        """Релятивистский γ-фактор"""
        try:
            if len(args) >= 1:
                velocity = float(self.calc.calculate(args[0]))
                gamma = self.physics.lorentz_factor(velocity)
                print(f"✅ γ-фактор для v={velocity:.2e} м/с: γ = {gamma:.6f}")
            else:
                print("❌ Использование: :lorentz скорость")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_kinetic(self, args: List[str]) -> bool:
        """Кинетическая энергия"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                velocity = float(self.calc.calculate(args[1]))
                
                energy = self.physics.kinetic_energy(mass, velocity)
                print(f"✅ Кинетическая энергия: E = ½·{mass}·{velocity}² = {energy:.6f} Дж")
            else:
                print("❌ Использование: :kinetic масса скорость")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_schwarzschild(self, args: List[str]) -> bool:
        """Радиус Шварцшильда"""
        try:
            if len(args) >= 1:
                mass = float(self.calc.calculate(args[0]))
                radius = self.physics.schwarzschild_radius(mass)
                print(f"✅ Радиус Шварцшильда для M={mass} кг: r = {radius:.2e} м")
            else:
                print("❌ Использование: :schwarzschild масса")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_orbital(self, args: List[str]) -> bool:
        """Орбитальная скорость"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                radius = float(self.calc.calculate(args[1]))
                
                velocity = self.physics.orbital_velocity(mass, radius)
                print(f"✅ Орбитальная скорость: v = √(G*{mass}/{radius}) = {velocity:.2f} м/с")
            else:
                print("❌ Использование: :orbital масса радиус")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_escape(self, args: List[str]) -> bool:
        """Вторая космическая скорость"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                radius = float(self.calc.calculate(args[1]))
                
                velocity = self.physics.escape_velocity(mass, radius)
                print(f"✅ Вторая космическая скорость: v = √(2G*{mass}/{radius}) = {velocity:.2f} м/с")
            else:
                print("❌ Использование: :escape масса радиус")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_solve(self, args: List[str]) -> bool:
        """Решение уравнения"""
        try:
            if len(args) >= 1:
                equation = ' '.join(args)
                variable = 'x'
                
                for arg in args:
                    if arg.isalpha() and len(arg) == 1:
                        variable = arg
                        break
                
                solutions = self.math.solve_equation(equation, variable)
                if solutions:
                    print(f"✅ Решения уравнения {equation}:")
                    for i, sol in enumerate(solutions):
                        print(f"  {variable}_{i+1} = {sol:.6f}")
                else:
                    print("❌ Уравнение не имеет действительных решений")
            else:
                print("❌ Использование: :solve уравнение [переменная]")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_derivative(self, args: List[str]) -> bool:
        """Производная функции"""
        try:
            if len(args) >= 1:
                full_cmd = ' '.join(args)
                
                variable = 'x'
                point = None
                
                if ' var=' in full_cmd:
                    parts = full_cmd.split(' var=')
                    expression = parts[0]
                    var_part = parts[1].split()[0] if ' ' in parts[1] else parts[1]
                    variable = var_part[0]
                elif ' point=' in full_cmd:
                    parts = full_cmd.split(' point=')
                    expression = parts[0]
                    point_str = parts[1].split()[0] if ' ' in parts[1] else parts[1]
                    point = float(point_str)
                else:
                    expression = full_cmd
                
                result = self.math.derivative(expression, variable, point)
                
                if point is not None:
                    print(f"✅ Производная {expression} по {variable} в точке {point}: {result:.6f}")
                else:
                    print(f"✅ Производная {expression} по {variable}: {result}")
            else:
                print("❌ Использование: :deriv выражение")
                print("💡 Примеры:")
                print("   :deriv x**3 + 2*x**2 - 5*x + 1")
                print("   :deriv sin(x) + cos(x) var=x")
                print("   :deriv x**2 point=2")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_integral(self, args: List[str]) -> bool:
        """Определенный интеграл"""
        try:
            if len(args) >= 3:
                expression = args[0]
                a = float(self.calc.calculate(args[1]))
                b = float(self.calc.calculate(args[2]))
                variable = args[3] if len(args) > 3 else 'x'
                
                result = self.math.definite_integral(expression, variable, (a, b))
                print(f"✅ Интеграл ∫[{a}→{b}] {expression} d{variable} = {result:.6f}")
            else:
                print("❌ Использование: :integral выражение нижний_предел верхний_предел [переменная]")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_stats(self, args: List[str]) -> bool:
        """Описательная статистика"""
        try:
            if len(args) >= 1:
                data_str = ' '.join(args)
                data_str = data_str.strip('[]')
                data = [float(x.strip()) for x in data_str.split(',')]
                
                stats_result = self.stats.descriptive_statistics(data)
                print("\n📊 ОПИСАТЕЛЬНАЯ СТАТИСТИКА:")
                for key, value in stats_result.items():
                    if math.isnan(value):
                        print(f"  {key:>12}: не определено")
                    else:
                        print(f"  {key:>12}: {value:.6f}")
            else:
                print("❌ Использование: :stats [значение1, значение2, ...]")
                
        except (CalculatorError, StatisticsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_regression(self, args: List[str]) -> bool:
        """Линейная регрессия"""
        try:
            if len(args) >= 2:
                x_str = args[0].strip('[]')
                y_str = args[1].strip('[]')
                
                x_data = [float(x.strip()) for x in x_str.split(',')]
                y_data = [float(y.strip()) for y in y_str.split(',')]
                
                regression_result = self.stats.linear_regression(x_data, y_data)
                
                print("\n📈 ЛИНЕЙНАЯ РЕГРЕССИЯ:")
                print(f"  Уравнение: y = {regression_result['slope']:.6f}x + {regression_result['intercept']:.6f}")
                print(f"  R² = {regression_result['r_squared']:.6f}")
                
                p_val = regression_result['p_value']
                if p_val < 1e-10:
                    print(f"  p-значение ≈ 0 (статистически значимо)")
                    print("  💡 p-значение очень мало, что указывает на сильную связь между переменными")
                else:
                    print(f"  p-значение = {p_val:.6f}")
                
                print(f"  Стандартная ошибка = {regression_result['std_error']:.6f}")
            else:
                print("❌ Использование: :regression [x1,x2,...] [y1,y2,...]")
                
        except (CalculatorError, StatisticsError, LicenseError) as e:
            print(f"❌ Ошибка: {e}")
        return True
    
    def _cmd_save(self, args: List[str]) -> bool:
        """Сохранение состояния"""
        try:
            filename = args[0] if args else "calculator_state.pkl"
            state = {
                'variables': self.calc.variables,
                'history': self.calc.history,
                'precision': self.calc.precision,
                'angle_mode': self.calc.angle_mode,
                'license_info': self.license_manager.get_license_info()
            }
            with open(filename, 'wb') as f:
                pickle.dump(state, f)
            print(f"✅ Состояние сохранено в {filename}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
        return True
    
    def _cmd_load(self, args: List[str]) -> bool:
        """Загрузка состояния"""
        try:
            filename = args[0] if args else "calculator_state.pkl"
            with open(filename, 'rb') as f:
                state = pickle.load(f)
            
            self.calc.variables = state.get('variables', {})
            self.calc.history = state.get('history', [])
            self.calc.precision = state.get('precision', 10)
            self.calc.angle_mode = state.get('angle_mode', 'rad')
            
            license_info = state.get('license_info', {})
            if license_info.get('valid') and license_info.get('key'):
                self.license_manager.license_key = license_info['key']
                self.license_manager.license_type = license_info['type']
                self.license_manager.license_valid = True
                self.license_manager.license_features = license_info.get('features', {})
            
            print(f"✅ Состояние загружено из {filename}")
            print(f"📖 Загружено {len(self.calc.history)} записей истории")
            
            if self.license_manager.license_valid:
                print(f"🔑 Лицензия {self.license_manager.license_type} восстановлена")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
        return True
    
    def _cmd_export_history(self, args: List[str]) -> bool:
        """Экспорт истории"""
        try:
            filename = args[0] if args else "calculator_history_export.txt"
            self.calc.export_history(filename)
        except (LicenseError, Exception) as e:
            print(f"❌ Ошибка экспорта: {e}")
        return True
    
    def _cmd_reset(self, args: List[str]) -> bool:
        """Сброс калькулятора"""
        self.calc.variables.clear()
        self.calc.history.clear()
        self.calc.precision = 10
        self.calc.angle_mode = 'rad'
        self.license_manager.reset_license()
        print("✅ Калькулятор сброшен до начального состояния")
        return True
    
    def handle_command(self, command: str) -> bool:
        """Обработка команды"""
        command = command.strip()
        
        if not command:
            return True
        
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        parts = command.split()
        cmd_key = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd_key in self.commands:
            return self.commands[cmd_key](args)
        else:
            print(f"❌ Неизвестная команда: {cmd_key}")
            print("💡 Введите :help для списка команд")
            return True
    
    def run(self):
        """Главный цикл выполнения"""
        print("🚀 Добро пожаловать в НАУЧНЫЙ КАЛЬКУЛЯТОР VIM-STYLE!")
        print("💡 Введите :help для справки, :q для выхода")
        print("🔑 Для доступа к премиум функциям активируйте лицензию: :activate КЛЮЧ")
        
        # Автозагрузка лицензии
        self.license_manager.auto_load()
        
        running = True
        while running:
            try:
                self.print_banner()
                
                if self.mode == "NORMAL":
                    prompt = ":[vsc] "
                    user_input = input(prompt).strip()
                    
                    if user_input.startswith(':'):
                        running = self.handle_command(user_input)
                    else:
                        running = self.handle_command(':' + user_input)
                        
                elif self.mode == "INSERT":
                    prompt = "EXPR> "
                    user_input = input(prompt).strip()
                    
                    if user_input.startswith(':'):
                        running = self.handle_command(user_input)
                    else:
                        try:
                            result = self.calc.calculate(user_input)
                            formatted_result = self.calc.format_result(result)
                            print(f"✅ РЕЗУЛЬТАТ: {formatted_result}")
                        except (CalculatorError, LicenseError) as e:
                            print(f"❌ ОШИБКА: {e}")
                
            except KeyboardInterrupt:
                print("\n\n💡 Для выхода введите :q")
            except EOFError:
                print("\n\n👋 До свидания!")
                self.calc._save_history()
                running = False
            except Exception as e:
                print(f"💥 Критическая ошибка: {e}")
                running = False

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    calculator = VimStyleCalculator()
    calculator.run()