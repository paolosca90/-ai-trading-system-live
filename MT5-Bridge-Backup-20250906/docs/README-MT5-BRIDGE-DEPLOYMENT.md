# MT5 Bridge VPS Deployment Documentation

**Server**: Windows VPS  
**Domain**: ai.cash-revolution.com  
**Backup Date**: 2025-09-06 11:27:56  

## 📋 Stack Overview

### Core Services
- **MT5 Bridge API**: Python FastAPI application (Port 8000)
- **NGINX**: Reverse proxy with SSL termination (Port 80/443)
- **win-acme**: Let's Encrypt SSL certificate management
- **Windows Task Scheduler**: Automated certificate renewal

### Directory Structure
```
C:\
├── nginx\                          # NGINX installation
│   ├── nginx.exe                   # NGINX executable
│   ├── conf\
│   │   └── nginx.conf              # Main configuration
│   ├── certs\                      # SSL certificates
│   │   ├── ai.cash-revolution.com-le.crt    # Let's Encrypt cert
│   │   ├── ai.cash-revolution.com-le.key    # Private key
│   │   └── ai.cash-revolution.com.pfx       # PFX format (win-acme)
│   ├── acme\                       # ACME challenge directory
│   │   └── .well-known\
│   │       └── acme-challenge\     # Let's Encrypt validation files
│   └── logs\                       # NGINX logs
│
├── win-acme\                       # SSL certificate manager
│   ├── wacs.exe                    # win-acme executable
│   ├── settings_default.json       # Default settings
│   └── Scripts\                    # Scripts directory
│
├── ProgramData\
│   └── win-acme\                   # win-acme configuration data
│       └── acme-v02.api.letsencrypt.org\  # Let's Encrypt account data
│
└── Users\Administrator\Desktop\
    └── mt5_bridge_vps\             # MT5 Bridge application directory
        ├── main.py                 # FastAPI application
        ├── requirements.txt        # Python dependencies
        └── [other MT5 bridge files]
```

## 🔌 Network Configuration

### Port Mapping
- **80 (HTTP)**: ACME challenges + HTTPS redirect
- **443 (HTTPS)**: SSL termination → proxy to port 8000
- **8000 (Internal)**: MT5 Bridge FastAPI application

### DNS Configuration
- **Domain**: ai.cash-revolution.com
- **A Record**: Points to server IP (154.61.187.189)

## 🔒 SSL/TLS Configuration

### Certificate Details
- **Provider**: Let's Encrypt
- **Certificate**: `/C=US/O=Let's Encrypt/CN=R13`
- **Subject**: `CN=ai.cash-revolution.com`
- **Valid**: Sep 6, 2025 - Dec 5, 2025
- **Auto-renewal**: Configured via Task Scheduler

### NGINX SSL Settings
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

## 🔄 Certificate Renewal

### win-acme Configuration
- **Renewal Schedule**: Daily at 09:00 with 4-hour random delay
- **Method**: HTTP-01 validation via filesystem
- **Webroot**: `C:/nginx/acme`
- **Task Name**: `win-acme renew (acme-v02.api.letsencrypt.org)`

### Renewal Command
```bash
cd "C:/win-acme"
./wacs.exe --renew --baseuri "https://acme-v02.api.letsencrypt.org/"
```

## 🌐 NGINX Configuration

### HTTP Server (Port 80)
- Serves ACME challenges from `C:/nginx/acme/.well-known/acme-challenge/`
- Redirects all other traffic to HTTPS

### HTTPS Server (Port 443)
- SSL termination with Let's Encrypt certificates
- Reverse proxy to MT5 Bridge on `http://127.0.0.1:8000`
- Proper headers forwarding for backend application

## 🚀 Service Management

### Starting Services
1. **MT5 Bridge**: Run from application directory
   ```bash
   cd C:/Users/Administrator/Desktop/mt5_bridge_vps
   python main.py
   ```

2. **NGINX**: 
   ```bash
   cd C:/nginx
   nginx.exe
   ```

### Stopping Services
1. **NGINX**:
   ```bash
   cd C:/nginx
   nginx.exe -s stop
   ```

2. **MT5 Bridge**: Stop the Python process

### Reloading NGINX Configuration
```bash
cd C:/nginx
nginx.exe -s reload
```

## 🔧 Troubleshooting

### Common Issues

1. **Certificate Renewal Fails**
   - Check ACME challenge directory permissions
   - Verify domain DNS resolution
   - Ensure NGINX is serving ACME challenges on port 80

2. **NGINX Won't Start**
   - Test configuration: `nginx.exe -t`
   - Check port 80/443 availability
   - Verify certificate file paths

3. **MT5 Bridge Connection Issues**
   - Check if application is running on port 8000
   - Verify proxy_pass configuration in nginx.conf
   - Check firewall settings

### Log Locations
- **NGINX Access**: `C:/nginx/logs/access.log`
- **NGINX Error**: `C:/nginx/logs/error.log`
- **win-acme**: Windows Event Log (Application)

## 📞 API Endpoints

### Health Check
- **URL**: `https://ai.cash-revolution.com/`
- **Response**: `{"service":"MT5 Bridge API","version":"1.0.0","status":"active"}`

### ACME Challenge Test
- **URL**: `http://ai.cash-revolution.com/.well-known/acme-challenge/test.txt`
- **Response**: `ACME challenge test file - OK`

## 🔐 Security Features

1. **HTTPS Enforcement**: All HTTP traffic redirected to HTTPS
2. **Modern TLS**: Only TLSv1.2 and TLSv1.3 supported
3. **Secure Headers**: Proper forwarding for backend application
4. **Certificate Validation**: Automated Let's Encrypt validation

## 📋 Backup Locations

All configurations backed up to: `/c/mt5_backup/20250906_112756/`

### Backup Contents
- `nginx/nginx.conf` - NGINX configuration
- `certificates/` - All SSL certificates and keys
- `win-acme/` - Complete win-acme installation
- `win-acme-data/` - win-acme configuration and account data
- `scripts/` - Windows Task Scheduler exports
- `docs/` - This documentation

---

**Last Updated**: September 6, 2025  
**Deployment Status**: ✅ Production Ready  
**SSL Status**: ✅ Valid Let's Encrypt Certificate  
**Auto-Renewal**: ✅ Configured