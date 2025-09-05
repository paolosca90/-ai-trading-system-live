import os
import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class MT5BridgeClient:
    """Client for communicating with MT5 Bridge service"""

    def __init__(self):
        self.base_url = os.getenv("BRIDGE_BASE_URL", "http://localhost:8000")
        self.api_key = os.getenv("BRIDGE_API_KEY", "your-bridge-api-key-change-this")
        self.timeout = 30

        # Remove trailing slash from base_url
        self.base_url = self.base_url.rstrip('/')

        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to bridge service"""
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(
                        url, 
                        headers=self.headers, 
                        timeout=self.timeout,
                        params=data
                    )
                else:
                    response = await client.request(
                        method,
                        url,
                        headers=self.headers,
                        json=data,
                        timeout=self.timeout
                    )

                # Check if request was successful
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise HTTPException(status_code=503, detail="Bridge authentication failed")
                elif response.status_code == 404:
                    raise HTTPException(status_code=503, detail="Bridge service not found")
                else:
                    try:
                        error_detail = response.json().get("detail", "Unknown bridge error")
                    except:
                        error_detail = f"Bridge returned status {response.status_code}"
                    raise HTTPException(status_code=503, detail=f"Bridge error: {error_detail}")

        except httpx.TimeoutException:
            logger.error(f"Timeout calling bridge endpoint {endpoint}")
            raise HTTPException(status_code=503, detail="Bridge service timeout")
        except httpx.ConnectError:
            logger.error(f"Connection error to bridge endpoint {endpoint}")
            raise HTTPException(status_code=503, detail="Bridge service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error calling bridge: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Bridge communication error: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Check bridge service health"""
        return await self._make_request("GET", "/health")

    async def initialize(self) -> Dict[str, Any]:
        """Initialize MT5 terminal"""
        return await self._make_request("POST", "/bridge/initialize")

    async def login(self, login: int, password: str, server: str, timeout: int = 60000) -> Dict[str, Any]:
        """Login to MT5 account"""
        data = {
            "login": login,
            "password": password,
            "server": server,
            "timeout": timeout
        }
        return await self._make_request("POST", "/bridge/login", data)

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return await self._make_request("GET", "/bridge/account")

    async def get_symbols(self) -> Dict[str, Any]:
        """Get available symbols"""
        return await self._make_request("GET", "/bridge/symbols")

    async def get_rates(
        self, 
        symbol: str, 
        timeframe: str = "H1", 
        count: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get historical rates"""
        data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": count
        }

        if date_from:
            data["date_from"] = date_from.isoformat()
        if date_to:
            data["date_to"] = date_to.isoformat()

        return await self._make_request("POST", "/bridge/rates", data)

    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        return await self._make_request("GET", "/bridge/positions")

    async def logout(self) -> Dict[str, Any]:
        """Logout and shutdown MT5"""
        return await self._make_request("POST", "/bridge/logout")

# Global client instance
mt5_client = MT5BridgeClient()
