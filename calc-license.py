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

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# ==================== LICENSE SYSTEM ====================

class LicenseManager:
    """License manager for calculator with device binding"""
    
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
        """Generate HMAC signature for data"""
        try:
            # Format JSON EXACTLY as on server
            # Server uses: json.dumps(data, sort_keys=True, separators=(',', ':'))
            payload_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            
            print(f"🔐 Data for signature: {payload_str}")
            
            # Decode base64 secret
            secret_bytes = base64.b64decode(self.hmac_secret)
            
            # Create HMAC signature
            signature = hmac.new(
                secret_bytes,
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            # Encode to base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            print(f"🔐 Generated signature: {signature_b64}")
            
            return signature_b64
            
        except Exception as e:
            print(f"⚠️ HMAC generation error: {e}")
            return ""
    
    def _load_verified_keys(self) -> Dict[str, Dict]:
        """Load verified keys from file"""
        try:
            if os.path.exists(self.verified_keys_file):
                with open(self.verified_keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_verified_keys(self):
        """Save verified keys to file"""
        try:
            with open(self.verified_keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.verified_keys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save verified_keys: {e}")
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        try:
            # Combine several identifiers for uniqueness
            system_info = f"{platform.node()}-{platform.system()}-{platform.processor()}"
            # Add MAC address if available
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,8*6,8)][::-1])
                system_info += f"-{mac}"
            except:
                pass
            
            # Create hash
            device_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
            return device_id
        except Exception:
            # Fallback - random ID
            return str(uuid.uuid4())[:16]
        
    def _get_default_features(self) -> Dict[str, bool]:
        """Return basic functions (without license)"""
        return {
            'basic_calculations': True,
            'trigonometry': True,
            'logarithms': True,
            'constants': True,
            'variables': True,
            'history': True,
            
            # Premium functions (require license)
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
        """Return functions depending on license type"""
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
        """Validate license on server with device binding"""
        try:
            print(f"🔐 Sending request to server: {self.license_server_url}")
            
            license_type = self._detect_license_type(license_key)
            
            payload = {
                'license_key': license_key,
                'license_type': license_type,
                'timestamp': datetime.utcnow().isoformat(),
                'client_info': f'calculator_{self.device_id}',
                'device_id': self.device_id
            }
            
            # Generate HMAC signature BEFORE sending
            signature = self._generate_hmac_signature(payload)
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
                'X-Signature': signature
            }
            
            print(f"📦 Data being sent: {json.dumps(payload, indent=2)}")
            print(f"🔐 HMAC signature: {signature}")
            print(f"📋 Headers: {headers}")
            
            response = requests.post(
                f"{self.license_server_url}/api/validate",
                json=payload,  # Send original payload
                headers=headers,
                timeout=10,
                verify=False
            )
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response body: {response.text}")
            print(f"📋 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    self._add_verified_key(license_key, license_type)
                    self.license_key = license_key
                    self.license_type = license_type
                    self.license_valid = True
                    self.license_features = self._get_license_features(license_type)
                    self._auto_save()
                    return True, f"✅ {license_type} license activated! Premium functions available."
                else:
                    return False, f"❌ License error: {data.get('message', 'Unknown error')}"
            elif response.status_code == 401:
                return False, "❌ Authentication error (401)"
            elif response.status_code == 403:
                return False, "❌ Access denied (403)"
            else:
                return False, f"❌ Server error: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ License validation error: {str(e)}"

    def _validate_with_ssl_bypass(self, license_key: str) -> Tuple[bool, str]:
        """License validation with disabled SSL verification"""
        try:
            print("⚠️  Using insecure connection (self-signed certificate)")
            
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
                    
                    return True, f"✅ {license_type} license activated! Premium functions available."
                else:
                    return False, f"❌ License error: {data.get('message', 'Unknown error')}"
            else:
                return self._validate_license_offline(license_key)
                
        except Exception as e:
            return False, f"❌ SSL connection error: {str(e)}"

    def _validate_with_certificate(self, license_key: str) -> Tuple[bool, str]:
        """License validation using certificate"""
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
            
            # Use certificate if it exists
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
                    
                    return True, f"✅ {license_type} license activated!"
                else:
                    return False, f"❌ License error: {data.get('message', 'Unknown error')}"
            else:
                return self._validate_license_offline(license_key)
                
        except requests.exceptions.SSLError:
            # If SSL error, try without verification
            return self._validate_with_ssl_bypass(license_key)
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"

    def _add_verified_key(self, license_key: str, license_type: str):
        """Add key to verified list"""
        self.verified_keys[license_key] = {
            'type': license_type,
            'verified_at': datetime.now().isoformat(),
            'device_id': self.device_id
        }
        self._save_verified_keys()
    
    def _is_key_verified(self, license_key: str) -> bool:
        """Check if key was verified by server"""
        return license_key in self.verified_keys
    
    def _detect_license_type(self, license_key: str) -> str:
        """Detect license type by key"""
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
        """Offline license validation - ONLY for verified keys"""
        # Check basic format
        if len(license_key) != 16:
            return False, "❌ Invalid license key format"
        
        # Check if key was verified by server
        if not self._is_key_verified(license_key):
            return False, "❌ Key not verified by server. Online activation required."
        
        # Get verified key information
        key_info = self.verified_keys.get(license_key, {})
        license_type = key_info.get('type', self._detect_license_type(license_key))
        
        # Check device binding
        saved_device_id = key_info.get('device_id')
        if saved_device_id and saved_device_id != self.device_id:
            return False, "❌ License bound to another device"
        
        self.license_key = license_key
        self.license_type = license_type
        self.license_valid = True
        self.license_features = self._get_license_features(license_type)
        
        # Auto-save on offline activation
        self._auto_save()
        
        return True, f"✅ {license_type} license activated (offline mode)"
    
    def _auto_save(self):
        """Auto-save license state"""
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
            print(f"⚠️ Failed to auto-save license: {e}")
    
    def auto_load(self) -> bool:
        """Auto-load license state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)
                
                # Check device binding
                saved_device_id = state.get('device_id')
                if saved_device_id != self.device_id:
                    print("⚠️ License bound to another device")
                    return False
                
                # Restore license
                self.license_key = state.get('license_key')
                self.license_type = state.get('license_type')
                self.license_valid = state.get('license_valid', False)
                self.license_features = state.get('license_features', self._get_default_features())
                
                # Check if key is still verified
                if self.license_valid and self.license_key and not self._is_key_verified(self.license_key):
                    print("⚠️ License no longer verified")
                    self.license_valid = False
                    return False
                
                if self.license_valid:
                    print(f"🔑 {self.license_type} license automatically restored")
                    return True
                    
        except Exception as e:
            print(f"⚠️ Failed to auto-load license: {e}")
        
        return False
    
    def has_feature(self, feature: str) -> bool:
        """Check feature availability"""
        return self.license_features.get(feature, False)
    
    def get_license_info(self) -> Dict[str, Any]:
        """Return license information"""
        verification_status = "✅ Verified" if self._is_key_verified(self.license_key) else "❌ Not verified" if self.license_key else "N/A"
        
        return {
            'valid': self.license_valid,
            'type': self.license_type,
            'key': self.license_key,
            'features': self.license_features,
            'device_id': self.device_id,
            'verified': verification_status
        }
    
    def reset_license(self):
        """Reset license"""
        self.license_key = None
        self.license_type = None
        self.license_valid = False
        self.license_features = self._get_default_features()
        
        # Delete state file
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
        except:
            pass

# ==================== EXCEPTION CLASSES ====================

class CalculatorError(Exception):
    """Base calculator exception"""
    pass

class CalculationError(CalculatorError):
    """Expression calculation error"""
    pass

class PhysicsError(CalculatorError):
    """Physics calculation error"""
    pass

class MathError(CalculatorError):
    """Math operations error"""
    pass

class StatisticsError(CalculatorError):
    """Statistics calculation error"""
    pass

class LicenseError(CalculatorError):
    """License error"""
    pass

# ==================== SAFE EVALUATOR ====================

class ExpressionParser:
    """Safe mathematical expression parser"""
    
    @staticmethod
    def tokenize(expression: str) -> List[str]:
        """Split expression into tokens"""
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
        """Check expression safety"""
        valid_chars = set('+-*/^().0123456789abcdefghijklmnopqrstuvwxyz_')
        for token in tokens:
            if not all(c in valid_chars for c in token.lower()):
                return False
        return True

class SafeEvaluator:
    """Safe expression evaluator"""
    
    def __init__(self, license_manager: LicenseManager):
        self.license_manager = license_manager
        self.functions = self._init_functions()
        self.constants = self._init_constants()
    
    def _init_functions(self) -> Dict[str, Any]:
        """Initialize safe functions"""
        functions = {
            # Trigonometry
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'atan2': math.atan2,
            
            # Exponents and logarithms
            'exp': math.exp, 'log': math.log, 'log10': math.log10, 
            'log2': math.log2, 'sqrt': math.sqrt, 'pow': math.pow,
            
            # Rounding
            'ceil': math.ceil, 'floor': math.floor, 'round': round,
            'abs': abs,
        }
        
        # Extended functions require license
        if self.license_manager.has_feature('advanced_functions'):
            functions.update({
                'gamma': math.gamma, 'lgamma': math.lgamma, 
                'factorial': math.factorial, 'erf': math.erf,
            })
            
        return functions
    
    def _init_constants(self) -> Dict[str, float]:
        """Initialize constants"""
        return {
            'pi': math.pi, 'e': math.e, 'tau': math.tau,
            'inf': float('inf'), 'nan': float('nan'),
        }
    
    def evaluate(self, expression: str, variables: Dict[str, float] = None, 
                high_precision: bool = False) -> float:
        """Safe expression evaluation"""
        # License check for high precision arithmetic
        if high_precision and not self.license_manager.has_feature('high_precision'):
            raise LicenseError("High precision requires license activation")
            
        try:
            # Preprocessing
            expr = self._preprocess_expression(expression)
            
            # Safety check
            tokens = ExpressionParser.tokenize(expr)
            if not ExpressionParser.is_valid_expression(tokens):
                raise CalculationError("Expression contains invalid characters")
            
            # Create environment
            env = {**self.constants, **self.functions}
            if variables:
                env.update(variables)
            
            # Compile and execute
            code = compile(expr, '<string>', 'eval')
            result = eval(code, {'__builtins__': {}}, env)
            
            if not isinstance(result, (int, float)):
                raise CalculationError("Result must be a number")
            
            # High precision via decimal
            if high_precision:
                if not self.license_manager.has_feature('high_precision'):
                    raise LicenseError("High precision requires PRO or BUSINESS license")
                    
                with decimal.localcontext() as ctx:
                    ctx.prec = 1000  # Very high precision for calculations
                    decimal_result = Decimal(str(result))
                    return float(decimal_result)
            else:
                return float(result)
            
        except SyntaxError as e:
            raise CalculationError(f"Syntax error: {e}")
        except NameError as e:
            raise CalculationError(f"Unknown variable or function: {e}")
        except ZeroDivisionError:
            raise CalculationError("Division by zero")
        except OverflowError:
            raise CalculationError("Calculation overflow")
        except Exception as e:
            raise CalculationError(f"Calculation error: {e}")

    def _preprocess_expression(self, expr: str) -> str:
        """Preprocess expression"""
        expr = expr.replace('^', '**')
        expr = expr.replace('π', 'pi')
        return expr

# ==================== CALCULATOR ====================

@dataclass
class CalculationResult:
    """Calculation result"""
    expression: str
    result: float
    timestamp: float
    success: bool = True
    error_message: str = ""

class ScientificCalculator:
    """Scientific calculator with history and variables"""
    
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
        """Initialize physical constants"""
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
        """Save history to file"""
        try:
            with open(self.history_file, 'wb') as f:
                pickle.dump(self.history, f)
        except Exception as e:
            print(f"⚠️ Warning: failed to save history: {e}")
    
    def _load_history(self):
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'rb') as f:
                    self.history = pickle.load(f)
                print(f"📖 Loaded {len(self.history)} records from history")
        except Exception as e:
            print(f"⚠️ Warning: failed to load history: {e}")
            self.history = []
    
    def calculate(self, expression: str) -> float:
        """Calculate expression with history saving"""
        try:
            # License check for extended functions
            if any(func in expression.upper() for func in ['GAMMA', 'LGAMMA', 'ERF']):
                if not self.license_manager.has_feature('advanced_functions'):
                    raise LicenseError("Extended mathematical functions require PRO or BUSINESS license")
            
            # Temporary variable replacement
            temp_vars = self.variables.copy()
            
            # Angle conversion for trigonometric functions
            if self.angle_mode != 'rad':
                temp_vars.update(self._get_angle_conversion_functions())
            
            # Use high precision if needed
            high_precision = self.precision > 15
            result = self.evaluator.evaluate(expression, temp_vars, high_precision)
            
            # Rounding considering high precision
            if self.precision > 15:
                if not self.license_manager.has_feature('high_precision'):
                    raise LicenseError("High precision (>15 digits) requires license")
                    
                with decimal.localcontext() as ctx:
                    ctx.prec = self.precision + 10
                    decimal_result = Decimal(str(result))
                    rounded_result = float(round(decimal_result, self.precision))
            else:
                rounded_result = round(result, self.precision)
            
            # Save to history
            calc_result = CalculationResult(
                expression=expression,
                result=rounded_result,
                timestamp=time.time()
            )
            self.history.append(calc_result)
            
            # Auto-save history
            if len(self.history) % 10 == 0:
                self._save_history()
            
            return rounded_result
            
        except (CalculationError, LicenseError) as e:
            # Save error to history
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
        """Get functions with angle conversion"""
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
        """Set variable"""
        if not name.isidentifier():
            raise CalculationError(f"Invalid variable name: {name}")
        self.variables[name] = value
    
    def get_history(self, limit: int = 10) -> List[CalculationResult]:
        """Get calculation history"""
        return self.history[-limit:] if limit else self.history
    
    def clear_history(self):
        """Clear history"""
        self.history.clear()
        self._save_history()
    
    def export_history(self, filename: str = "calculator_history_export.txt"):
        """Export history to text file"""
        if not self.license_manager.has_feature('export_features'):
            raise LicenseError("History export requires BUSINESS license")
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CALCULATION HISTORY\n")
                f.write("=" * 50 + "\n")
                for i, result in enumerate(self.history):
                    status = "SUCCESS" if result.success else "ERROR"
                    f.write(f"{i+1:4d}. [{status}] {result.expression}\n")
                    if result.success:
                        if self.precision > 15:
                            f.write(f"     Result: {result.result:.15f}...\n")
                        else:
                            f.write(f"     Result: {result.result}\n")
                    else:
                        f.write(f"     Error: {result.error_message}\n")
                    time_str = datetime.fromtimestamp(result.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"     Time: {time_str}\n")
                    f.write("-" * 50 + "\n")
            print(f"✅ History exported to {filename}")
        except Exception as e:
            print(f"❌ History export error: {e}")
    
    def format_result(self, result: float) -> str:
        """Format result considering current precision"""
        if self.precision > 15:
            display_precision = min(self.precision, 50)
            return f"{result:.{display_precision}f}"
        else:
            return f"{result}"

# ==================== PHYSICS ENGINE ====================

class PhysicsEngine:
    """Physics calculation engine"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Check license for physics calculations"""
        if not self.license_manager.has_feature('physics_engine'):
            raise LicenseError("Physics calculations require license activation")
    
    def pendulum_period(self, length: float, gravity: float = None) -> float:
        """Period of mathematical pendulum"""
        self._check_license()
        
        if length <= 0:
            raise PhysicsError("Pendulum length must be positive")
        
        if gravity is None:
            gravity = self.calc.variables.get('g', 9.80665)
        
        if gravity <= 0:
            raise PhysicsError("Gravity acceleration must be positive")
        
        return 2 * math.pi * math.sqrt(length / gravity)
    
    def lorentz_factor(self, velocity: float) -> float:
        """Relativistic γ-factor"""
        self._check_license()
        
        c = self.calc.variables.get('c', 299792458)
        
        if abs(velocity) >= c:
            raise PhysicsError("Velocity cannot exceed speed of light")
        
        return 1 / math.sqrt(1 - (velocity / c) ** 2)
    
    def kinetic_energy(self, mass: float, velocity: float) -> float:
        """Kinetic energy"""
        self._check_license()
        
        if mass < 0:
            raise PhysicsError("Mass cannot be negative")
        
        return 0.5 * mass * velocity ** 2
    
    def schwarzschild_radius(self, mass: float) -> float:
        """Schwarzschild radius"""
        self._check_license()
        
        if mass <= 0:
            raise PhysicsError("Mass must be positive")
        
        G = self.calc.variables.get('G', 6.67430e-11)
        c = self.calc.variables.get('c', 299792458)
        
        return 2 * G * mass / (c ** 2)
    
    def orbital_velocity(self, mass: float, radius: float) -> float:
        """Orbital velocity"""
        self._check_license()
        
        if mass <= 0 or radius <= 0:
            raise PhysicsError("Mass and radius must be positive")
        
        G = self.calc.variables.get('G', 6.67430e-11)
        return math.sqrt(G * mass / radius)
    
    def escape_velocity(self, mass: float, radius: float) -> float:
        """Escape velocity"""
        self._check_license()
        
        if mass <= 0 or radius <= 0:
            raise PhysicsError("Mass and radius must be positive")
        
        return math.sqrt(2) * self.orbital_velocity(mass, radius)

# ==================== MATH ENGINE ====================

class MathEngine:
    """Mathematical calculation engine"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Check license for mathematical calculations"""
        if not self.license_manager.has_feature('math_engine'):
            raise LicenseError("Mathematical calculations require license activation")
    
    def solve_equation(self, equation: str, variable: str = 'x') -> List[float]:
        """Solve algebraic equation"""
        self._check_license()
        
        try:
            var = symbols(variable)
            
            if '=' in equation:
                parts = equation.split('=')
                if len(parts) == 2:
                    left, right = parts
                    expr = sp.sympify(f"({left}) - ({right})")
                else:
                    raise MathError("Invalid equation format")
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
            raise MathError(f"Equation solving error: {e}")
    
    def derivative(self, expression: str, variable: str = 'x', point: float = None) -> Union[str, float]:
        """Calculate derivative"""
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
            raise MathError(f"Derivative calculation error: {e}")
    
    def definite_integral(self, expression: str, variable: str = 'x', 
                         limits: Tuple[float, float] = None) -> float:
        """Calculate definite integral"""
        self._check_license()
        
        if limits is None:
            raise MathError("Integration limits not specified")
        
        try:
            a, b = limits
            var = symbols(variable)
            expr = sp.sympify(expression)
            
            result = sp_integrate(expr, (var, a, b))
            return float(result.evalf())
            
        except Exception as e:
            raise MathError(f"Integral calculation error: {e}")

# ==================== STATISTICS ENGINE ====================

class StatisticsEngine:
    """Statistical calculation engine"""
    
    def __init__(self, calculator: ScientificCalculator, license_manager: LicenseManager):
        self.calc = calculator
        self.license_manager = license_manager
    
    def _check_license(self):
        """Check license for statistical calculations"""
        if not self.license_manager.has_feature('statistics_engine'):
            raise LicenseError("Statistical calculations require license activation")
    
    def validate_data(self, data: List[float]) -> None:
        """Validate input data"""
        if not data:
            raise StatisticsError("Data cannot be empty")
        
        if len(data) < 2:
            raise StatisticsError("Insufficient data for statistical analysis")
        
        if any(math.isnan(x) or math.isinf(x) for x in data):
            raise StatisticsError("Data contains NaN or infinities")
    
    def descriptive_statistics(self, data: List[float]) -> Dict[str, float]:
        """Descriptive statistics"""
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
            raise StatisticsError(f"Statistics calculation error: {e}")
    
    def linear_regression(self, x_data: List[float], y_data: List[float]) -> Dict[str, float]:
        """Linear regression"""
        self._check_license()
        
        if len(x_data) != len(y_data):
            raise StatisticsError("x and y array sizes must match")
        
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
            raise StatisticsError(f"Linear regression error: {e}")

# ==================== Vim-STYLE INTERFACE ====================

class VimStyleCalculator:
    """Calculator with Vim-like interface"""
    
    def __init__(self):
        self.license_manager = LicenseManager()
        self.calc = ScientificCalculator(self.license_manager)
        self.physics = PhysicsEngine(self.calc, self.license_manager)
        self.math = MathEngine(self.calc, self.license_manager)
        self.stats = StatisticsEngine(self.calc, self.license_manager)
        
        self.mode = "NORMAL"
        self.command_history: List[str] = []
        self.history_index = -1
        
        # Command registration
        self.commands = self._register_commands()
    
    def _register_commands(self) -> Dict[str, Any]:
        """Register all available commands"""
        return {
            # Basic commands
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
            
            # License
            ':license': self._cmd_license,
            ':activate': self._cmd_activate,
            ':license_info': self._cmd_license_info,
            
            # Variables
            ':vars': self._cmd_vars,
            ':let': self._cmd_let,
            ':del': self._cmd_del,
            
            # Physics
            ':pendulum': self._cmd_pendulum,
            ':lorentz': self._cmd_lorentz,
            ':kinetic': self._cmd_kinetic,
            ':schwarzschild': self._cmd_schwarzschild,
            ':orbital': self._cmd_orbital,
            ':escape': self._cmd_escape,
            
            # Mathematics
            ':solve': self._cmd_solve,
            ':deriv': self._cmd_derivative,
            ':integral': self._cmd_integral,
            
            # Statistics
            ':stats': self._cmd_stats,
            ':regression': self._cmd_regression,
            
            # System
            ':save': self._cmd_save,
            ':load': self._cmd_load,
            ':reset': self._cmd_reset,
            ':export_history': self._cmd_export_history,
        }
    
    def print_banner(self):
        """Print banner"""
        license_info = self.license_manager.get_license_info()
        license_status = "✅ ACTIVATED" if license_info['valid'] else "❌ MISSING"
        license_type = license_info['type'] or "DEMO"
        
        precision_warning = ""
        if self.calc.precision > 50:
            precision_warning = " ⚠️ HIGH PRECISION"
        elif self.calc.precision > 15:
            precision_warning = " ⚠️"
        
        banner = f"""
╔════════════════════════════════════════════════════════════════╗
║                   VIM SCIENTIFIC CALCULATOR                    ║
║                        MODE: {self.mode:<8}                         ║
║                   LICENSE: {license_type:<9} {license_status:<18} ║
║                   PRECISION: {self.calc.precision} digits{precision_warning:<18}        ║
║                   ANGLES: {self.calc.angle_mode:<4}                                   ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_help(self):
        """Show help"""
        license_info = self.license_manager.get_license_info()
        
        help_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                       CALCULATOR COMMANDS                      ║
║                    LICENSE: {license_info['type'] or 'DEMO':<10}                          ║
╚════════════════════════════════════════════════════════════════╗

🎯 BASIC COMMANDS:
  :q, :quit, :exit           - Exit
  :h, :help                  - Help
  :m normal|insert        - Change mode
  :clear                     - Clear screen
  :history [N]               - Calculation history
  :precision N               - Set precision (1-1000)
  :angle rad|deg|grad        - Angle mode

🔑 LICENSE COMMANDS:
  :license                   - License information
  :activate KEY             - Activate license
  :license_info              - Detailed information

📊 VARIABLES:
  :vars                      - Show variables
  :let var = expression        - Set variable
  :del var                   - Delete variable

🚀 PHYSICS COMMANDS: {'✅' if license_info['features']['physics_engine'] else '❌'}
  :pendulum L [g]            - Pendulum period
  :lorentz v                 - Relativistic γ-factor
  :kinetic m v               - Kinetic energy
  :schwarzschild M           - Schwarzschild radius
  :orbital M r               - Orbital velocity
  :escape M r                - Escape velocity

🧮 MATHEMATICS COMMANDS: {'✅' if license_info['features']['math_engine'] else '❌'}
  :solve equation [var]     - Solve equation
  :deriv expression [var] [x] - Derivative
  :integral expression a b    - Definite integral

📈 STATISTICS COMMANDS: {'✅' if license_info['features']['statistics_engine'] else '❌'}
  :stats data              - Descriptive statistics
  :regression x_data y_data  - Linear regression

💾 SYSTEM COMMANDS:
  :save [file]               - Save state
  :load [file]               - Load state
  :reset                     - Reset calculator
  :export_history [file]     - Export history to file {'✅' if license_info['features']['export_features'] else '❌'}

📝 EXAMPLES:
  :m insert
  2 + 3 * sin(pi/4)
  :let r = 6371e3
  :activate YOUR_LICENSE_KEY
  :pendulum 1
  :stats [1,2,3,4,5]
  :solve x**2 - 4 = 0

💡 AVAILABLE LICENSES:
  🎓 STUDENT  - Basic scientific functions
  ⚡ PRO      - Extended mathematical functions  
  🏢 BUSINESS - Full functionality + export
        """
        print(help_text)
    
    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    # ==================== COMMAND IMPLEMENTATIONS ====================
    
    def _cmd_quit(self, args: List[str]) -> bool:
        """Exit command"""
        print("👋 Goodbye!")
        self.calc._save_history()
        return False
    
    def _cmd_help(self, args: List[str]) -> bool:
        """Help command"""
        self.show_help()
        return True
    
    def _cmd_mode(self, args: List[str]) -> bool:
        """Change mode"""
        if len(args) >= 1:
            mode = args[0].upper()
            if mode in ['NORMAL', 'INSERT']:
                self.mode = mode
                print(f"✅ Mode changed to: {mode}")
            else:
                print("❌ Error: available modes - normal, insert")
        else:
            print("❌ Usage: :mode normal|insert")
        return True
    
    def _cmd_clear(self, args: List[str]) -> bool:
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    
    def _cmd_history(self, args: List[str]) -> bool:
        """Calculation history"""
        try:
            limit = int(args[0]) if args else 10
            history = self.calc.get_history(limit)
            
            print(f"\n📜 CALCULATION HISTORY (last {len(history)} of {len(self.calc.history)}):")
            for i, result in enumerate(history):
                status = "✅" if result.success else "❌"
                if result.success:
                    formatted_result = self.calc.format_result(result.result)
                    print(f"  {i+1:2d}. {status} {result.expression} = {formatted_result}")
                else:
                    print(f"  {i+1:2d}. {status} {result.expression} -> ERROR: {result.error_message}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_precision(self, args: List[str]) -> bool:
        """Set precision"""
        if len(args) >= 1:
            try:
                precision = int(args[0])
                if 1 <= precision <= 1000:
                    if precision > 15 and not self.license_manager.has_feature('custom_precision'):
                        print("❌ Error: high precision requires license activation")
                        print("💡 Available licenses: STUDENT, PRO, BUSINESS")
                        return True
                    
                    if precision > 50:
                        print("⚠️  WARNING: High precision set!")
                        print("   This may slow down calculations and use more memory")
                        confirm = input("   Continue? (y/N): ")
                        if confirm.lower() != 'y':
                            print("❌ Precision setting cancelled")
                            return True
                    
                    if precision > 100:
                        print(f"⚠️  VERY high precision set: {precision} digits")
                        print("   Calculations may be slow")
                    
                    old_precision = self.calc.precision
                    self.calc.precision = precision
                    print(f"✅ Precision changed: {old_precision} -> {precision} digits")
                    
                    if precision > 15:
                        print("💡 To view full result use :history")
                        print("💡 Calculations now use high-precision arithmetic")
                else:
                    print("❌ Error: precision must be from 1 to 1000")
            except ValueError:
                print("❌ Error: precision must be an integer")
        else:
            print("❌ Usage: :precision number")
        return True
    
    def _cmd_angle(self, args: List[str]) -> bool:
        """Set angle mode"""
        if len(args) >= 1:
            mode = args[0].lower()
            if mode in ['rad', 'deg', 'grad']:
                self.calc.angle_mode = mode
                print(f"✅ Angle mode set: {mode}")
            else:
                print("❌ Error: available modes - rad, deg, grad")
        else:
            print("❌ Usage: :angle rad|deg|grad")
        return True
    
    def _cmd_license(self, args: List[str]) -> bool:
        """License information"""
        license_info = self.license_manager.get_license_info()
        
        print("\n🔑 LICENSE INFORMATION:")
        print(f"  Status: {'✅ ACTIVATED' if license_info['valid'] else '❌ MISSING'}")
        print(f"  Type: {license_info['type'] or 'DEMO'}")
        print(f"  Key: {license_info['key'] or 'Not activated'}")
        
        print("\n📋 AVAILABLE FUNCTIONS:")
        features = license_info['features']
        for feature, enabled in features.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {self._get_feature_description(feature)}")
        
        if not license_info['valid']:
            print("\n💡 To activate, enter: :activate YOUR_LICENSE_KEY")
            print("🎓 STUDENT - Basic scientific functions")
            print("⚡ PRO     - Extended mathematical functions")  
            print("🏢 BUSINESS - Full functionality + export")
        
        return True
    
    def _cmd_activate(self, args: List[str]) -> bool:
        """License activation"""
        if len(args) >= 1:
            license_key = args[0]
            success, message = self.license_manager.validate_license(license_key)
            
            print(message)
            
            if success:
                self.calc = ScientificCalculator(self.license_manager, self.calc.precision, self.calc.angle_mode)
                self.physics = PhysicsEngine(self.calc, self.license_manager)
                self.math = MathEngine(self.calc, self.license_manager)
                self.stats = StatisticsEngine(self.calc, self.license_manager)
                
                print("🎉 Congratulations! Premium functions now available!")
                self._cmd_license([])
        else:
            print("❌ Usage: :activate LICENSE_KEY")
            print("💡 Example: :activate BUS123456789ABCDE")
        
        return True
    
    def _cmd_license_info(self, args: List[str]) -> bool:
        """Detailed license information"""
        license_info = self.license_manager.get_license_info()
        
        print("\n🔑 DETAILED LICENSE INFORMATION:")
        print(f"  Status: {'✅ ACTIVATED' if license_info['valid'] else '❌ MISSING'}")
        print(f"  Type: {license_info['type'] or 'DEMO'}")
        print(f"  Key: {license_info['key'] or 'Not activated'}")
        
        print("\n🎯 LICENSE LEVELS:")
        print("  🎓 STUDENT  - Basic scientific functions")
        print("     • Calculations with normal precision")
        print("     • Physics calculations")
        print("     • Statistical functions")
        print("     • Equation solving")
        
        print("\n  ⚡ PRO      - Extended capabilities")
        print("     • Everything from STUDENT +")
        print("     • High precision (up to 1000 digits)")
        print("     • Symbolic calculations")
        print("     • Extended mathematical functions")
        
        print("\n  🏢 BUSINESS - Professional level")
        print("     • Everything from PRO +")
        print("     • History and data export")
        print("     • Priority support")
        
        return True
    
    def _get_feature_description(self, feature: str) -> str:
        """Return feature description"""
        descriptions = {
            'basic_calculations': 'Basic calculations',
            'trigonometry': 'Trigonometric functions',
            'logarithms': 'Logarithms and exponents',
            'constants': 'Mathematical constants',
            'variables': 'Variable operations',
            'history': 'Calculation history',
            'high_precision': 'High precision (>15 digits)',
            'physics_engine': 'Physics calculations',
            'math_engine': 'Mathematical engines',
            'statistics_engine': 'Statistical calculations',
            'symbolic_math': 'Symbolic calculations',
            'advanced_functions': 'Extended functions',
            'export_features': 'Data export',
            'custom_precision': 'Precision customization',
        }
        return descriptions.get(feature, feature)
    
    def _cmd_vars(self, args: List[str]) -> bool:
        """Show variables"""
        print("\n📊 VARIABLES:")
        for var, val in self.calc.variables.items():
            print(f"  {var} = {val}")
        
        if not self.calc.variables:
            print("  (no user variables)")
        return True
    
    def _cmd_let(self, args: List[str]) -> bool:
        """Set variable"""
        try:
            if len(args) >= 3 and args[1] == '=':
                var_name = args[0]
                expr = ' '.join(args[2:])
                
                result = self.calc.calculate(expr)
                self.calc.set_variable(var_name, result)
                formatted_result = self.calc.format_result(result)
                print(f"✅ Set: {var_name} = {formatted_result}")
            else:
                print("❌ Usage: :let variable = expression")
                
        except (CalculatorError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_del(self, args: List[str]) -> bool:
        """Delete variable"""
        if len(args) >= 1:
            var_name = args[0]
            if var_name in self.calc.variables:
                del self.calc.variables[var_name]
                print(f"✅ Deleted variable: {var_name}")
            else:
                print(f"❌ Error: variable '{var_name}' not found")
        else:
            print("❌ Usage: :del variable_name")
        return True
    
    def _cmd_pendulum(self, args: List[str]) -> bool:
        """Pendulum period"""
        try:
            if len(args) >= 1:
                length = float(self.calc.calculate(args[0]))
                gravity = float(self.calc.calculate(args[1])) if len(args) > 1 else None
                
                period = self.physics.pendulum_period(length, gravity)
                print(f"✅ Pendulum period: T = 2π√({length}/{gravity or 'g'}) = {period:.6f} s")
            else:
                print("❌ Usage: :pendulum length [gravity_acceleration]")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_lorentz(self, args: List[str]) -> bool:
        """Relativistic γ-factor"""
        try:
            if len(args) >= 1:
                velocity = float(self.calc.calculate(args[0]))
                gamma = self.physics.lorentz_factor(velocity)
                print(f"✅ γ-factor for v={velocity:.2e} m/s: γ = {gamma:.6f}")
            else:
                print("❌ Usage: :lorentz velocity")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_kinetic(self, args: List[str]) -> bool:
        """Kinetic energy"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                velocity = float(self.calc.calculate(args[1]))
                
                energy = self.physics.kinetic_energy(mass, velocity)
                print(f"✅ Kinetic energy: E = ½·{mass}·{velocity}² = {energy:.6f} J")
            else:
                print("❌ Usage: :kinetic mass velocity")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_schwarzschild(self, args: List[str]) -> bool:
        """Schwarzschild radius"""
        try:
            if len(args) >= 1:
                mass = float(self.calc.calculate(args[0]))
                radius = self.physics.schwarzschild_radius(mass)
                print(f"✅ Schwarzschild radius for M={mass} kg: r = {radius:.2e} m")
            else:
                print("❌ Usage: :schwarzschild mass")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_orbital(self, args: List[str]) -> bool:
        """Orbital velocity"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                radius = float(self.calc.calculate(args[1]))
                
                velocity = self.physics.orbital_velocity(mass, radius)
                print(f"✅ Orbital velocity: v = √(G*{mass}/{radius}) = {velocity:.2f} m/s")
            else:
                print("❌ Usage: :orbital mass radius")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_escape(self, args: List[str]) -> bool:
        """Escape velocity"""
        try:
            if len(args) >= 2:
                mass = float(self.calc.calculate(args[0]))
                radius = float(self.calc.calculate(args[1]))
                
                velocity = self.physics.escape_velocity(mass, radius)
                print(f"✅ Escape velocity: v = √(2G*{mass}/{radius}) = {velocity:.2f} m/s")
            else:
                print("❌ Usage: :escape mass radius")
                
        except (CalculatorError, PhysicsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_solve(self, args: List[str]) -> bool:
        """Solve equation"""
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
                    print(f"✅ Solutions for equation {equation}:")
                    for i, sol in enumerate(solutions):
                        print(f"  {variable}_{i+1} = {sol:.6f}")
                else:
                    print("❌ Equation has no real solutions")
            else:
                print("❌ Usage: :solve equation [variable]")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_derivative(self, args: List[str]) -> bool:
        """Function derivative"""
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
                    print(f"✅ Derivative of {expression} by {variable} at point {point}: {result:.6f}")
                else:
                    print(f"✅ Derivative of {expression} by {variable}: {result}")
            else:
                print("❌ Usage: :deriv expression")
                print("💡 Examples:")
                print("   :deriv x**3 + 2*x**2 - 5*x + 1")
                print("   :deriv sin(x) + cos(x) var=x")
                print("   :deriv x**2 point=2")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_integral(self, args: List[str]) -> bool:
        """Definite integral"""
        try:
            if len(args) >= 3:
                expression = args[0]
                a = float(self.calc.calculate(args[1]))
                b = float(self.calc.calculate(args[2]))
                variable = args[3] if len(args) > 3 else 'x'
                
                result = self.math.definite_integral(expression, variable, (a, b))
                print(f"✅ Integral ∫[{a}→{b}] {expression} d{variable} = {result:.6f}")
            else:
                print("❌ Usage: :integral expression lower_limit upper_limit [variable]")
                
        except (CalculatorError, MathError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_stats(self, args: List[str]) -> bool:
        """Descriptive statistics"""
        try:
            if len(args) >= 1:
                data_str = ' '.join(args)
                data_str = data_str.strip('[]')
                data = [float(x.strip()) for x in data_str.split(',')]
                
                stats_result = self.stats.descriptive_statistics(data)
                print("\n📊 DESCRIPTIVE STATISTICS:")
                for key, value in stats_result.items():
                    if math.isnan(value):
                        print(f"  {key:>12}: not defined")
                    else:
                        print(f"  {key:>12}: {value:.6f}")
            else:
                print("❌ Usage: :stats [value1, value2, ...]")
                
        except (CalculatorError, StatisticsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_regression(self, args: List[str]) -> bool:
        """Linear regression"""
        try:
            if len(args) >= 2:
                x_str = args[0].strip('[]')
                y_str = args[1].strip('[]')
                
                x_data = [float(x.strip()) for x in x_str.split(',')]
                y_data = [float(y.strip()) for y in y_str.split(',')]
                
                regression_result = self.stats.linear_regression(x_data, y_data)
                
                print("\n📈 LINEAR REGRESSION:")
                print(f"  Equation: y = {regression_result['slope']:.6f}x + {regression_result['intercept']:.6f}")
                print(f"  R² = {regression_result['r_squared']:.6f}")
                
                p_val = regression_result['p_value']
                if p_val < 1e-10:
                    print(f"  p-value ≈ 0 (statistically significant)")
                    print("  💡 p-value is very small, indicating strong relationship between variables")
                else:
                    print(f"  p-value = {p_val:.6f}")
                
                print(f"  Standard error = {regression_result['std_error']:.6f}")
            else:
                print("❌ Usage: :regression [x1,x2,...] [y1,y2,...]")
                
        except (CalculatorError, StatisticsError, LicenseError) as e:
            print(f"❌ Error: {e}")
        return True
    
    def _cmd_save(self, args: List[str]) -> bool:
        """Save state"""
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
            print(f"✅ State saved to {filename}")
        except Exception as e:
            print(f"❌ Save error: {e}")
        return True
    
    def _cmd_load(self, args: List[str]) -> bool:
        """Load state"""
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
            
            print(f"✅ State loaded from {filename}")
            print(f"📖 Loaded {len(self.calc.history)} history records")
            
            if self.license_manager.license_valid:
                print(f"🔑 {self.license_manager.license_type} license restored")
        except Exception as e:
            print(f"❌ Load error: {e}")
        return True
    
    def _cmd_export_history(self, args: List[str]) -> bool:
        """Export history"""
        try:
            filename = args[0] if args else "calculator_history_export.txt"
            self.calc.export_history(filename)
        except (LicenseError, Exception) as e:
            print(f"❌ Export error: {e}")
        return True
    
    def _cmd_reset(self, args: List[str]) -> bool:
        """Reset calculator"""
        self.calc.variables.clear()
        self.calc.history.clear()
        self.calc.precision = 10
        self.calc.angle_mode = 'rad'
        self.license_manager.reset_license()
        print("✅ Calculator reset to initial state")
        return True
    
    def handle_command(self, command: str) -> bool:
        """Handle command"""
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
            print(f"❌ Unknown command: {cmd_key}")
            print("💡 Enter :help for command list")
            return True
    
    def run(self):
        """Main execution loop"""
        print("🚀 Welcome to VIM-STYLE SCIENTIFIC CALCULATOR!")
        print("💡 Enter :help for help, :q to exit")
        print("🔑 For premium functions, activate license: :activate KEY")
        
        # Auto-load license
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
                            print(f"✅ RESULT: {formatted_result}")
                        except (CalculatorError, LicenseError) as e:
                            print(f"❌ ERROR: {e}")
                
            except KeyboardInterrupt:
                print("\n\n💡 To exit, enter :q")
            except EOFError:
                print("\n\n👋 Goodbye!")
                self.calc._save_history()
                running = False
            except Exception as e:
                print(f"💥 Critical error: {e}")
                running = False

# ==================== LAUNCH ====================

if __name__ == "__main__":
    calculator = VimStyleCalculator()
    calculator.run()