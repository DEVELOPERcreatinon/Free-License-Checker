# License Server System

![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red.svg)
![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

## Overview

A secure and scalable license key management server built with Flask. This system provides robust license validation, key generation, and administration features with enterprise-grade security measures.

## Features

- **Secure License Validation**: HMAC-signed requests and API key authentication
- **Multiple License Types**: Support for BUSINESS, PRO, and STUDENT licenses
- **Database Security**: Encrypted SQLite database storage
- **Rate Limiting**: Configurable request limiting per IP address
- **Comprehensive Logging**: Detailed request and error logging with log rotation
- **Administration API**: Secure endpoints for key generation and statistics
- **Health Monitoring**: Built-in health check endpoints
- **IP Restrictions**: Configurable IP whitelisting and blacklisting

## License Information

All source code files (except `config.json`) are licensed under the **Mozilla Public License 2.0**. See the LICENSE file for complete terms.

## System Requirements

- Python 3.11.9 (Tested version)
- SQLite 3.35.0 or higher
- OpenSSL (for manual SSL certificate generation)

## Installation

### 1. Clone or Download the Project

```bash
git clone https://github.com/DEVELOPERcreatinon/Free-Licence-Checker.git
cd Free-Licence-Checker
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

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

Or install all at once:

```bash
pip install Flask==2.3.3 Flask-Limiter==3.3.0 Flask-JWT-Extended==4.5.3 cryptography==41.0.7 SQLAlchemy==2.0.23 Werkzeug==2.3.7 python-dotenv==1.0.0 pyjwt==2.8.0
```

## Configuration

### 1. Initial Setup

Before running the server, generate secure keys:

```bash
python generate_keys.py
```

This script will:
- Generate secure encryption keys for the database
- Create a JWT secret for admin authentication
- Generate HMAC secrets for request signing
- Create secure API keys

### 2. Generating SSL Certificates with OpenSSL (Windows)

#### Option A: Using Windows Subsystem for Linux (WSL)
If you have WSL installed, OpenSSL is typically available:

```bash
# In WSL terminal
openssl version
# Should show: OpenSSL 3.0.x or similar

# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Copy to Windows directory (adjust path)
cp cert.pem key.pem /mnt/c/path/to/your/project/
```

#### Option B: Using Git Bash
Git for Windows includes OpenSSL:

```bash
# Open Git Bash
cd /c/path/to/your/project

# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Option C: Using PowerShell with Chocolatey
Install OpenSSL via Chocolatey package manager:

```powershell
# Install Chocolatey if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install OpenSSL
choco install openssl

# Generate certificate (after adding OpenSSL to PATH)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Option D: Using Windows Native OpenSSL (Manual Installation)

1. Download OpenSSL for Windows from [slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
2. Install to `C:\OpenSSL-Win64`
3. Add to system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Environment Variables → System Variables → Path → Edit
   - Add `C:\OpenSSL-Win64\bin`
4. Generate certificates in Command Prompt:

```cmd
cd C:\path\to\your\project
C:\OpenSSL-Win64\bin\openssl.exe req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Option E: Generate Without OpenSSL (Python)
Create a simple Python script `generate_ssl.py`:

```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

# Generate certificate
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

# Write private key
with open("key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Write certificate
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("SSL certificates generated: cert.pem and key.pem")
```

Run it:
```bash
python generate_ssl.py
```

### 3. Verify SSL Certificates

Check if certificates are properly generated:

```bash
# Check certificate details
openssl x509 -in cert.pem -text -noout

# Verify key matches certificate
openssl rsa -in key.pem -check
```

### 4. Configuration File

Update your `config.json` to use the generated certificates:

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

## Running the Server

### 1. Start the License Server

```bash
python run.py
```

The server will perform security checks and start on the configured host and port.

### 2. Health Check

Verify the server is running with SSL:

```bash
curl -k https://localhost:5000/health
```

Note: `-k` flag ignores self-signed certificate warnings. For production, use valid certificates.

## API Endpoints

### License Validation

**Endpoint:** `POST /api/validate`

**Headers:**
- `X-API-Key`: Your API key
- `X-Signature`: HMAC signature (if require_encrypted_communication is true)

**Request Body:**
```json
{
    "license_key": "BUS1234567890ABCD",
    "license_type": "BUSINESS",
    "timestamp": "2024-01-01T00:00:00Z",
    "client_info": "Client Application v1.0"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "License validated successfully",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Generate License Keys (Admin Only)

**Endpoint:** `POST /api/admin/generate-keys`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
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

### Get Statistics (Admin Only)

**Endpoint:** `GET /api/admin/stats`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Response:**
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

## Key Format

License keys follow a specific format:
- **BUSINESS**: Starts with "BUS" (e.g., BUS1234567890ABC)
- **PRO**: Starts with "PRO" (e.g., PRO1234567890ABC)
- **STUDENT**: Starts with "STU" (e.g., STU1234567890ABC)

Total key length is 16 characters.

## Local Key Generation

Generate keys without HTTP requests:

```bash
python key.py
```

This will:
1. Generate keys for all license types
2. Save them to `generated_keys.json`
3. Show generation statistics

## Security Considerations

### 1. Default Keys
The system will warn you if default keys are detected. Always run `generate_keys.py` before production use.

### 2. HMAC Signatures
When `require_encrypted_communication` is enabled, all requests must include a valid HMAC signature.

### 3. API Keys
Multiple API keys can be configured for different clients.

### 4. JWT Tokens
Admin endpoints require JWT tokens with admin privileges.

### 5. IP Restrictions
Configure allowed IPs to restrict access to specific networks.

### 6. SSL Certificates
- For development: Self-signed certificates are acceptable
- For production: Obtain certificates from trusted Certificate Authorities (CA)
- Consider using Let's Encrypt for free production certificates

## Database Schema

The system uses two main tables:

### LicenseKeys Table
- `key_hash`: SHA256 hash of the license key
- `license_type`: Type of license (BUSINESS, PRO, STUDENT)
- `expiration_date`: License expiry date
- `is_active`: Whether the license is active
- `is_used`: Whether the license has been used
- `activation_count`: Number of activations
- `max_activations`: Maximum allowed activations

### ActivationLogs Table
- `key_hash`: Reference to license key
- `activation_date`: When activation occurred
- `client_ip`: Client IP address
- `success`: Whether activation succeeded
- `reason`: Reason for success/failure

## Logging

Logs are written to `license_server.log` with rotation:
- Maximum file size: 100MB
- Backup count: 5 files
- Log level configurable in `config.json`

## Rate Limiting

Rate limiting is enabled by default:
- 600 requests per minute per IP
- Uses fixed-window strategy
- Configurable in `config.json`

## Troubleshooting

### Common Issues

1. **"config.json not found!"**
   - Run `python generate_keys.py` first

2. **"SECURITY WARNINGS"**
   - Default keys detected. Run `python generate_keys.py` to generate secure keys

3. **Database errors**
   - Ensure SQLite is installed
   - Check file permissions for `licenses.db`

4. **SSL certificate errors**
   - Ensure `cert.pem` and `key.pem` exist in the project root
   - Or disable SSL in `config.json` by setting `"ssl_enabled": false`

5. **OpenSSL not found on Windows**
   - Use Git Bash (includes OpenSSL)
   - Install via Chocolatey: `choco install openssl`
   - Use the Python script alternative

6. **Certificate generation errors**
   - Ensure you have write permissions in the project directory
   - Check that OpenSSL version is 1.1.1 or higher
   - Try the Python-based certificate generation script

7. **Browser SSL warnings**
   - For development: Accept the self-signed certificate
   - For testing: Add certificate to trusted store
   - For production: Use valid certificates from a CA

### Checking Logs

```bash
# Windows Command Prompt
type license_server.log

# PowerShell
Get-Content license_server.log -Tail 50

# Git Bash/Linux
tail -f license_server.log
```

## Testing

The system has been tested with:
- Python 3.11.9
- SQLite 3.35.0+
- Various client implementations

For production deployment, additional testing is recommended for:
- Load testing
- Security penetration testing
- Database backup and restore procedures

## Backup and Maintenance

### Database Backups
- Enable in `config.json`: `"backup_enabled": true`
- Configure interval: `"backup_interval_hours": 24`

### SSL Certificate Renewal
Self-signed certificates expire after 365 days. To renew:

```bash
# Generate new certificates
openssl req -x509 -newkey rsa:4096 -keyout key_new.pem -out cert_new.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Backup old certificates
mv cert.pem cert.pem.backup
mv key.pem key.pem.backup

# Replace with new certificates
mv cert_new.pem cert.pem
mv key_new.pem key.pem

# Restart server
```

### Monitoring
- Use `/health` endpoint for health checks
- Monitor log files for errors
- Track rate limiting statistics

## Support

For issues or questions:
1. Check the logs in `license_server.log`
2. Verify configuration in `config.json`
3. Ensure all security keys are properly generated
4. Review API documentation for correct request formats
5. For SSL issues, verify certificates exist and are readable

## Version Compatibility

This system is specifically tested with Python 3.11.9. Using other Python versions may require dependency adjustments or code modifications.

## Additional Resources

- [OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html)
- [Let's Encrypt](https://letsencrypt.org/) - Free SSL certificates
- [Chocolatey Package Manager](https://chocolatey.org/)
- [Git for Windows](https://gitforwindows.org/) - Includes Git Bash with OpenSSL
