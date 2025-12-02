# Система Сервера Лицензий

![Лицензия: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red.svg)
![Статус: Готово к продакшену](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

[Русская версия](ru/readme.md)
[Английская версия](https://github.com/DEVELOPERcreatinon/Free-Licence-Checker/blob/main/readme.md)

## Обзор

Безопасный и масштабируемый сервер управления лицензионными ключами, построенный на Flask. Эта система предоставляет надежную валидацию лицензий, генерацию ключей и функции администрирования с корпоративными мерами безопасности.

## Функции

- **Безопасная валидация лицензий**: Подписанные HMAC запросы и аутентификация по API-ключам
- **Несколько типов лицензий**: Поддержка лицензий BUSINESS, PRO и STUDENT
- **Безопасность базы данных**: Зашифрованное хранение в SQLite базе данных
- **Ограничение запросов (Rate Limiting)**: Настраиваемое ограничение запросов на IP-адрес
- **Комплексное логирование**: Подробное логирование запросов и ошибок с ротацией логов
- **Административный API**: Безопасные эндпоинты для генерации ключей и статистики
- **Мониторинг здоровья**: Встроенные эндпоинты для проверки состояния
- **Ограничения по IP**: Настраиваемые белые и черные списки IP-адресов

## Информация о лицензии

Все файлы исходного кода (кроме `config.json`) лицензированы под **Mozilla Public License 2.0**. Полные условия смотрите в файле LICENSE.

## Системные требования

- Python 3.11.9 (Протестированная версия)
- SQLite 3.35.0 или выше
- OpenSSL (для ручной генерации SSL сертификатов)

## Установка

### 1. Клонируйте или скачайте проект

```bash
git clone https://github.com/DEVELOPERcreatinon/Free-Licence-Checker.git
cd Free-Licence-Checker
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # В Windows: venv\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install Flask==2.3.3
pip install Flask-Limiter==3.3.0
pip install Flask-JWT-Extended==4.5.3
pip install cryptography==41.0.7
pip install SQLAlchemy==2.0.23
pip install Werkzeug==2.3.7
pip install python-dotenv==1.0.0
pip install pyjwt==2.8.0
```

Или установите все сразу:

```bash
pip install Flask==2.3.3 Flask-Limiter==3.3.0 Flask-JWT-Extended==4.5.3 cryptography==41.0.7 SQLAlchemy==2.0.23 Werkzeug==2.3.7 python-dotenv==1.0.0 pyjwt==2.8.0
```

## Конфигурация

### 1. Начальная настройка

Перед запуском сервера сгенерируйте безопасные ключи:

```bash
python generate_keys.py
```

Этот скрипт:
- Сгенерирует безопасные ключи шифрования для базы данных
- Создаст JWT секрет для аутентификации администратора
- Сгенерирует HMAC секреты для подписи запросов
- Создаст безопасные API-ключи

### 2. Генерация SSL сертификатов с помощью OpenSSL (Windows)

#### Вариант A: Использование Windows Subsystem for Linux (WSL)
Если у вас установлен WSL, OpenSSL обычно доступен:

```bash
# В терминале WSL
openssl version
# Должно показать: OpenSSL 3.0.x или подобное

# Сгенерировать приватный ключ и сертификат
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Скопировать в директорию Windows (настройте путь)
cp cert.pem key.pem /mnt/c/path/to/your/project/
```

#### Вариант B: Использование Git Bash
Git для Windows включает OpenSSL:

```bash
# Откройте Git Bash
cd /c/path/to/your/project

# Сгенерировать приватный ключ и сертификат
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Вариант C: Использование PowerShell с Chocolatey
Установите OpenSSL через менеджер пакетов Chocolatey:

```powershell
# Установите Chocolatey если не установлен
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Установите OpenSSL
choco install openssl

# Сгенерируйте сертификат (после добавления OpenSSL в PATH)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Вариант D: Использование нативного OpenSSL для Windows (Ручная установка)

1. Скачайте OpenSSL для Windows с [slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
2. Установите в `C:\OpenSSL-Win64`
3. Добавьте в системный PATH:
   - Правый клик на "Этот компьютер" → Свойства → Дополнительные параметры системы
   - Переменные среды → Системные переменные → Path → Изменить
   - Добавьте `C:\OpenSSL-Win64\bin`
4. Сгенерируйте сертификаты в Командной строке:

```cmd
cd C:\path\to\your\project
C:\OpenSSL-Win64\bin\openssl.exe req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Вариант E: Генерация без OpenSSL (Python)
Создайте простой Python скрипт `generate_ssl.py`:

```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

# Сгенерировать приватный ключ
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

# Сгенерировать сертификат
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Organization"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.utcnow()
).not_valid_after(
    datetime.utcnow() + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Записать приватный ключ
with open("key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Записать сертификат
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("SSL сертификаты сгенерированы: cert.pem и key.pem")
```

Запустите его:
```bash
python generate_ssl.py
```

### 3. Проверьте SSL сертификаты

Проверьте, правильно ли сгенерированы сертификаты:

```bash
# Проверить детали сертификата
openssl x509 -in cert.pem -text -noout

# Проверить, что ключ соответствует сертификату
openssl rsa -in key.pem -check
```

### 4. Файл конфигурации

Обновите ваш `config.json`, чтобы использовать сгенерированные сертификаты:

```json
"server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "ssl_enabled": true,
    "ssl_cert_path": "cert.pem",
    "ssl_key_path": "key.pem"
}
```

## Запуск сервера

### 1. Запустите сервер лицензий

```bash
python run.py
```

Сервер выполнит проверки безопасности и запустится на настроенном хосте и порту.

### 2. Проверка здоровья

Убедитесь, что сервер работает с SSL:

```bash
curl -k https://localhost:5000/health
```

Примечание: флаг `-k` игнорирует предупреждения о самоподписанных сертификатах. Для продакшена используйте валидные сертификаты.

## API эндпоинты

### Валидация лицензии

**Эндпоинт:** `POST /api/validate`

**Заголовки:**
- `X-API-Key`: Ваш API-ключ
- `X-Signature`: HMAC подпись (если require_encrypted_communication равен true)

**Тело запроса:**
```json
{
    "license_key": "BUS1234567890ABCD",
    "license_type": "BUSINESS",
    "timestamp": "2024-01-01T00:00:00Z",
    "client_info": "Client Application v1.0"
}
```

**Ответ:**
```json
{
    "status": "success",
    "message": "License validated successfully",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Генерация лицензионных ключей (только для админа)

**Эндпоинт:** `POST /api/admin/generate-keys`

**Заголовки:**
- `Authorization: Bearer <jwt_token>`

**Ответ:**
```json
{
    "status": "success",
    "message": "Keys generated successfully",
    "results": {
        "BUSINESS": {
            "success_count": 100,
            "total_attempted": 100,
            "keys": ["BUS123...", "BUS456..."]
        }
    }
}
```

### Получение статистики (только для админа)

**Эндпоинт:** `GET /api/admin/stats`

**Заголовки:**
- `Authorization: Bearer <jwt_token>`

**Ответ:**
```json
{
    "status": "success",
    "stats": {
        "total_keys": 300,
        "active_keys": 250,
        "used_keys": 50,
        "expired_keys": 20
    }
}
```

## Формат ключей

Лицензионные ключи следуют определенному формату:
- **BUSINESS**: Начинается с "BUS" (например, BUS1234567890ABC)
- **PRO**: Начинается с "PRO" (например, PRO1234567890ABC)
- **STUDENT**: Начинается с "STU" (например, STU1234567890ABC)

Общая длина ключа - 16 символов.

## Локальная генерация ключей

Генерация ключей без HTTP запросов:

```bash
python key.py
```

Это:
1. Сгенерирует ключи для всех типов лицензий
2. Сохранит их в `generated_keys.json`
3. Покажет статистику генерации

## Вопросы безопасности

### 1. Ключи по умолчанию
Система предупредит вас, если обнаружены ключи по умолчанию. Всегда запускайте `generate_keys.py` перед использованием в продакшене.

### 2. HMAC подписи
Когда `require_encrypted_communication` включен, все запросы должны содержать валидную HMAC подпись.

### 3. API-ключи
Можно настроить несколько API-ключей для разных клиентов.

### 4. JWT токены
Административные эндпоинты требуют JWT токенов с правами администратора.

### 5. Ограничения по IP
Настройте разрешенные IP-адреса для ограничения доступа к определенным сетям.

### 6. SSL сертификаты
- Для разработки: Самоподписанные сертификаты приемлемы
- Для продакшена: Получите сертификаты от доверенных Центров Сертификации (CA)
- Рассмотрите использование Let's Encrypt для бесплатных продакшен сертификатов

## Схема базы данных

Система использует две основные таблицы:

### Таблица LicenseKeys
- `key_hash`: SHA256 хэш лицензионного ключа
- `license_type`: Тип лицензии (BUSINESS, PRO, STUDENT)
- `expiration_date`: Дата истечения лицензии
- `is_active`: Активна ли лицензия
- `is_used`: Использована ли лицензия
- `activation_count`: Количество активаций
- `max_activations`: Максимально разрешенное количество активаций

### Таблица ActivationLogs
- `key_hash`: Ссылка на лицензионный ключ
- `activation_date`: Когда произошла активация
- `client_ip`: IP-адрес клиента
- `success`: Успешна ли активация
- `reason`: Причина успеха/неудачи

## Логирование

Логи записываются в `license_server.log` с ротацией:
- Максимальный размер файла: 100MB
- Количество резервных копий: 5 файлов
- Уровень логирования настраивается в `config.json`

## Ограничение запросов (Rate Limiting)

Ограничение запросов включено по умолчанию:
- 600 запросов в минуту на IP-адрес
- Использует стратегию fixed-window
- Настраивается в `config.json`

## Решение проблем

### Частые проблемы

1. **"config.json not found!"**
   - Сначала запустите `python generate_keys.py`

2. **"SECURITY WARNINGS"**
   - Обнаружены ключи по умолчанию. Запустите `python generate_keys.py` для генерации безопасных ключей

3. **Ошибки базы данных**
   - Убедитесь, что SQLite установлен
   - Проверьте права на файл для `licenses.db`

4. **Ошибки SSL сертификатов**
   - Убедитесь, что `cert.pem` и `key.pem` существуют в корне проекта
   - Или отключите SSL в `config.json`, установив `"ssl_enabled": false`

5. **OpenSSL не найден в Windows**
   - Используйте Git Bash (включает OpenSSL)
   - Установите через Chocolatey: `choco install openssl`
   - Используйте альтернативный Python скрипт

6. **Ошибки генерации сертификатов**
   - Убедитесь, что у вас есть права на запись в директории проекта
   - Проверьте, что версия OpenSSL 1.1.1 или выше
   - Попробуйте скрипт генерации сертификатов на Python

7. **Предупреждения SSL в браузере**
   - Для разработки: Примите самоподписанный сертификат
   - Для тестирования: Добавьте сертификат в доверенное хранилище
   - Для продакшена: Используйте валидные сертификаты от CA

### Проверка логов

```bash
# Windows Command Prompt
type license_server.log

# PowerShell
Get-Content license_server.log -Tail 50

# Git Bash/Linux
tail -f license_server.log
```

## Тестирование

Система протестирована с:
- Python 3.11.9
- SQLite 3.35.0+
- Различными клиентскими реализациями

Для развертывания в продакшене рекомендуется дополнительное тестирование:
- Нагрузочное тестирование
- Тестирование на проникновение (пентест)
- Процедуры резервного копирования и восстановления базы данных

## Резервное копирование и обслуживание

### Резервное копирование базы данных
- Включите в `config.json`: `"backup_enabled": true`
- Настройте интервал: `"backup_interval_hours": 24`

### Обновление SSL сертификатов
Самоподписанные сертификаты истекают через 365 дней. Для обновления:

```bash
# Сгенерировать новые сертификаты
openssl req -x509 -newkey rsa:4096 -keyout key_new.pem -out cert_new.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Сделать резервную копию старых сертификатов
mv cert.pem cert.pem.backup
mv key.pem key.pem.backup

# Заменить новыми сертификатами
mv cert_new.pem cert.pem
mv key_new.pem key.pem

# Перезапустить сервер
```

### Мониторинг
- Используйте эндпоинт `/health` для проверки состояния
- Мониторьте файлы логов на наличие ошибок
- Отслеживайте статистику ограничения запросов

## Поддержка

При возникновении проблем или вопросов:
1. Проверьте логи в `license_server.log`
2. Проверьте конфигурацию в `config.json`
3. Убедитесь, что все ключи безопасности правильно сгенерированы
4. Просмотрите документацию API для правильных форматов запросов
5. При проблемах с SSL, убедитесь, что сертификаты существуют и доступны для чтения

## Совместимость версий

Эта система специально протестирована с Python 3.11.9. Использование других версий Python может потребовать корректировки зависимостей или модификации кода.

## Дополнительные ресурсы

- [OpenSSL для Windows](https://slproweb.com/products/Win32OpenSSL.html)
- [Let's Encrypt](https://letsencrypt.org/) - Бесплатные SSL сертификаты
- [Chocolatey Package Manager](https://chocolatey.org/)
- [Git для Windows](https://gitforwindows.org/) - Включает Git Bash с OpenSSL
