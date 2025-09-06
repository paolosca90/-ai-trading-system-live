@echo off
REM MT5 Bridge Backup Script
REM Run as Administrator

set BACKUP_ROOT=C:\MT5_Backups
set TIMESTAMP=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set BACKUP_DIR=%BACKUP_ROOT%\%TIMESTAMP%

echo Creating backup directory: %BACKUP_DIR%
mkdir "%BACKUP_DIR%\nginx"
mkdir "%BACKUP_DIR%\certificates"
mkdir "%BACKUP_DIR%\win-acme-data"
mkdir "%BACKUP_DIR%\scripts"
mkdir "%BACKUP_DIR%\docs"

echo Backing up NGINX configuration...
copy "C:\nginx\conf\nginx.conf" "%BACKUP_DIR%\nginx\"
xcopy /E /I "C:\nginx\acme" "%BACKUP_DIR%\nginx\acme"

echo Backing up certificates...
xcopy /E "C:\nginx\certs\*" "%BACKUP_DIR%\certificates\"

echo Backing up win-acme...
xcopy /E /I "C:\win-acme" "%BACKUP_DIR%\win-acme"
xcopy /E /I "C:\ProgramData\win-acme" "%BACKUP_DIR%\win-acme-data"

echo Exporting scheduled tasks...
schtasks /query /tn "win-acme renew (acme-v02.api.letsencrypt.org)" /xml > "%BACKUP_DIR%\scripts\win-acme-renewal-task.xml"
schtasks /query /tn "win-acme renew (acme-v02.api.letsencrypt.org)" /fo LIST > "%BACKUP_DIR%\scripts\win-acme-renewal-task-details.txt"

echo Creating backup summary...
echo Backup created: %date% %time% > "%BACKUP_DIR%\backup-info.txt"
echo Server: %COMPUTERNAME% >> "%BACKUP_DIR%\backup-info.txt"
echo User: %USERNAME% >> "%BACKUP_DIR%\backup-info.txt"
curl -s https://ai.cash-revolution.com/ >> "%BACKUP_DIR%\backup-info.txt" 2>nul

echo.
echo ================================
echo Backup completed successfully!
echo Location: %BACKUP_DIR%
echo ================================
echo.

pause