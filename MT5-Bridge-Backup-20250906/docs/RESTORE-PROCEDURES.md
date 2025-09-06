# MT5 Bridge Restore Procedures

## 🔄 Complete System Restore

### Prerequisites
- Windows Server/VPS
- Administrator access
- Domain DNS pointing to new server IP

### Step 1: Install NGINX
```bash
# Download NGINX for Windows
# Extract to C:/nginx/
mkdir C:/nginx
# Copy nginx.exe and basic structure
```

### Step 2: Restore NGINX Configuration
```bash
# Copy backed up nginx.conf
copy "backup/nginx/nginx.conf" "C:/nginx/conf/nginx.conf"

# Restore ACME directory structure
xcopy /E "backup/nginx/acme" "C:/nginx/acme/"

# Test configuration
cd C:/nginx
nginx.exe -t
```

### Step 3: Restore Certificates
```bash
# Create certificates directory
mkdir "C:/nginx/certs"

# Copy all certificate files
xcopy /E "backup/certificates/*" "C:/nginx/certs/"

# Verify certificate files exist:
# - ai.cash-revolution.com-le.crt
# - ai.cash-revolution.com-le.key
# - ai.cash-revolution.com.pfx
```

### Step 4: Install win-acme
```bash
# Create win-acme directory
mkdir "C:/win-acme"

# Extract win-acme from backup
xcopy /E "backup/win-acme/*" "C:/win-acme/"

# Restore configuration data
xcopy /E "backup/win-acme-data/*" "C:/ProgramData/win-acme/"

# Test win-acme
cd C:/win-acme
wacs.exe --version
```

### Step 5: Restore Task Scheduler
```powershell
# Import the renewal task
schtasks /create /xml "backup/scripts/win-acme-renewal-task.xml" /tn "win-acme renew (acme-v02.api.letsencrypt.org)"

# Verify task was created
schtasks /query /tn "win-acme*"
```

### Step 6: Start Services
```bash
# Start NGINX
cd C:/nginx
nginx.exe

# Verify NGINX is running
curl http://localhost/.well-known/acme-challenge/test.txt

# Start MT5 Bridge (in separate terminal)
cd "C:/path/to/mt5_bridge_vps"
python main.py
```

### Step 7: Verify HTTPS
```bash
# Test certificate
curl -I https://ai.cash-revolution.com/

# Check certificate details
openssl s_client -connect ai.cash-revolution.com:443 -servername ai.cash-revolution.com
```

## 🔧 Partial Restore Scenarios

### Restore Only Certificates
1. Copy certificate files to `C:/nginx/certs/`
2. Update nginx.conf paths if needed
3. Reload NGINX: `nginx.exe -s reload`

### Restore Only NGINX Configuration
1. Copy `nginx.conf` to `C:/nginx/conf/`
2. Test configuration: `nginx.exe -t`
3. Reload: `nginx.exe -s reload`

### Restore Only win-acme
1. Copy win-acme directory to `C:/win-acme/`
2. Copy ProgramData to `C:/ProgramData/win-acme/`
3. Import task scheduler XML
4. Test renewal: `wacs.exe --test`

## 🚨 Emergency Certificate Renewal

If certificates are expired or corrupted:

```bash
# Stop NGINX temporarily
cd C:/nginx
nginx.exe -s stop

# Create temporary self-signed certificate
openssl req -x509 -newkey rsa:2048 -keyout temp.key -out temp.crt -days 1 -nodes -subj "/CN=ai.cash-revolution.com"

# Update nginx.conf to use temporary certificates
# Start NGINX
nginx.exe

# Request new Let's Encrypt certificate
cd C:/win-acme
wacs.exe --source manual --host ai.cash-revolution.com --validation filesystem --webroot "C:/nginx/acme" --accepttos --emailaddress admin@cash-revolution.com --force

# Update nginx.conf to use new certificates
# Reload NGINX
nginx.exe -s reload
```

## ✅ Verification Checklist

After restore, verify:

- [ ] NGINX configuration test passes: `nginx.exe -t`
- [ ] HTTP ACME challenge accessible: `http://domain/.well-known/acme-challenge/test.txt`
- [ ] HTTPS certificate valid: `curl -I https://domain/`
- [ ] MT5 Bridge API responsive: `https://domain/` returns JSON
- [ ] win-acme task scheduled: Check Task Scheduler
- [ ] Certificate expiry date: Should be ~3 months from restore date

## 📞 Contact Information

- **Domain Registrar**: [Update with actual registrar]
- **DNS Provider**: [Update with actual DNS provider]
- **VPS Provider**: [Update with actual VPS provider]
- **Let's Encrypt Account Email**: admin@cash-revolution.com

---

**Created**: September 6, 2025  
**Last Updated**: September 6, 2025  
**Tested**: ✅ Procedures verified