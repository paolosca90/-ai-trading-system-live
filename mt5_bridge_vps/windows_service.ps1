# PowerShell script to create Windows Service for MT5 Bridge
# Run as Administrator

# Download NSSM (Non-Sucking Service Manager)
# https://nssm.cc/download

# Install service
nssm install MT5Bridge "C:\Python310\python.exe"
nssm set MT5Bridge Parameters "C:\path\to\your\main_bridge.py"
nssm set MT5Bridge AppDirectory "C:\path\to\your\bridge\directory"
nssm set MT5Bridge DisplayName "MT5 Trading Bridge"
nssm set MT5Bridge Description "MetaTrader 5 Bridge Service for Trading API"
nssm set MT5Bridge Start SERVICE_AUTO_START

# Set environment variables
nssm set MT5Bridge AppEnvironmentExtra API_KEY=your-api-key-here
nssm set MT5Bridge AppEnvironmentExtra LOG_LEVEL=INFO

# Configure logging
nssm set MT5Bridge AppStdout "C:\logs\mt5bridge_stdout.log"
nssm set MT5Bridge AppStderr "C:\logs\mt5bridge_stderr.log"
nssm set MT5Bridge AppRotateFiles 1
nssm set MT5Bridge AppRotateOnline 1
nssm set MT5Bridge AppRotateSeconds 86400
nssm set MT5Bridge AppRotateBytes 1048576

# Start service
nssm start MT5Bridge

# Check service status
nssm status MT5Bridge

# Useful commands:
# nssm stop MT5Bridge
# nssm restart MT5Bridge
# nssm remove MT5Bridge confirm
