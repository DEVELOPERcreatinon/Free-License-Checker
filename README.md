# License Server System

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

## Installation

### 1. Clone or Download the Project

```bash
git clone https://github.com/DEVELOPERcreatinon/Free-Licence-Checker.git
cd license-server
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

### 2. Configuration File

The `config.json` file contains all system settings. Key sections:

#### Server Configuration
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

#### Security Settings
```json
"security": {
    "api_key_required": true,
    "api_keys": ["your_api_keys_here"],
    "rate_limiting_enabled": true,
    "max_requests_per_minute": 600,
    "jwt_secret": "your_jwt_secret",
    "hmac_secret": "your_hmac_secret"
}
```

#### License Types
```json
"licensing": {
    "license_types": ["BUSINESS", "PRO", "STUDENT"],
    "key_length": 16,
    "default_validity_days": 30
}
```

## Running the Server

### 1. Start the License Server

```bash
python run.py
```

The server will perform security checks and start on the configured host and port.

### 2. Health Check

Verify the server is running:

```bash
curl https://localhost:5000/health
```

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
   - Or disable SSL in `config.json`

5. **HMAC signature errors**
   - Ensure client and server use the same HMAC secret
   - Verify data formatting matches exactly

### Checking Logs

```bash
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

## Version Compatibility

This system is specifically tested with Python 3.11.9. Using other Python versions may require dependency adjustments or code modifications.
