@echo off
REM Quick MT5 Bridge Status Check

echo ================================
echo MT5 Bridge System Status Check
echo ================================
echo.

echo [1/6] Checking NGINX process...
tasklist /FI "IMAGENAME eq nginx.exe" 2>nul | find /I "nginx.exe" && echo NGINX: RUNNING || echo NGINX: NOT RUNNING

echo.
echo [2/6] Checking port 443 (HTTPS)...
netstat -an | find ":443" && echo Port 443: LISTENING || echo Port 443: NOT LISTENING

echo.
echo [3/6] Testing HTTPS certificate...
echo Checking certificate expiry...
timeout /t 1 >nul
curl -I https://ai.cash-revolution.com/ 2>nul | find "HTTP" && echo HTTPS: OK || echo HTTPS: ERROR

echo.
echo [4/6] Testing ACME challenge...
curl -s http://ai.cash-revolution.com/.well-known/acme-challenge/test.txt 2>nul | find "ACME challenge test" && echo ACME Challenge: OK || echo ACME Challenge: ERROR

echo.
echo [5/6] Checking win-acme task...
schtasks /query /tn "win-acme*" 2>nul | find "win-acme" && echo win-acme Task: SCHEDULED || echo win-acme Task: NOT FOUND

echo.
echo [6/6] Testing MT5 Bridge API...
curl -s https://ai.cash-revolution.com/ 2>nul | find "MT5 Bridge API" && echo MT5 Bridge: OK || echo MT5 Bridge: ERROR

echo.
echo ================================
echo Status check completed!
echo ================================

pause