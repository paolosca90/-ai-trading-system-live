# Dockerfile for MT5 Bridge (if using Linux with Wine)
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y     python3     python3-pip     wine     wget     curl     && rm -rf /var/lib/apt/lists/*

# Set up Wine
ENV WINEPREFIX=/wine
ENV WINEARCH=win64
RUN wine wineboot --init

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application
COPY main_bridge.py .
COPY .env .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3     CMD curl -f -H "X-API-Key: $API_KEY" http://localhost:8000/health || exit 1

# Run application
CMD ["python3", "main_bridge.py"]
