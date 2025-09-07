#!/usr/bin/env python3
"""
Test MT5 Bridge Connection and Real Quotes
Utility script to test and debug MT5 integration issues
"""

import httpx
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MT5_BRIDGE_URL = os.getenv("MT5_BRIDGE_URL", "http://ai.cash-revolution.com:8000")
MT5_BRIDGE_API_KEY = os.getenv("MT5_BRIDGE_API_KEY", "1d2376ae63aedb38f4d13e1041fb5f0b56cc48c44a8f106194d2da23e4039736")

async def test_mt5_bridge_connection():
    """Test connection to MT5 Bridge service"""
    print(f"Testing MT5 Bridge connection to: {MT5_BRIDGE_URL}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            print("\n1. Testing Health Endpoint...")
            response = await client.get(f"{MT5_BRIDGE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Bridge Status: {data.get('status')}")
                print(f"MT5 Initialized: {data.get('mt5_initialized')}")
                print(f"Current Login: {data.get('current_login', 'None')}")
                print(f"Timestamp: {data.get('timestamp')}")
                return True
            else:
                print(f"Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Connection error: {e}")
        return False

async def test_mt5_quotes():
    """Test getting MT5 quotes"""
    print(f"\n2. Testing MT5 Quotes Retrieval...")
    
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"]
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"X-API-Key": MT5_BRIDGE_API_KEY}
            
            for symbol in symbols:
                print(f"\n   📊 Getting rates for {symbol}...")
                
                rates_request = {
                    "symbol": symbol,
                    "timeframe": "M1",
                    "count": 1
                }
                
                response = await client.post(
                    f"{MT5_BRIDGE_URL}/bridge/rates",
                    json=rates_request,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("rates") and len(data["rates"]) > 0:
                        latest_rate = data["rates"][-1]
                        print(f"   {symbol}: Close={latest_rate['close']}, Time={latest_rate['time']}")
                    else:
                        print(f"   {symbol}: No rate data available")
                else:
                    error_data = await response.atext()
                    print(f"   {symbol}: Error {response.status_code} - {error_data}")
                    
    except Exception as e:
        print(f"Quotes retrieval error: {e}")

async def test_account_info():
    """Test getting MT5 account information"""
    print(f"\n3. Testing MT5 Account Information...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"X-API-Key": MT5_BRIDGE_API_KEY}
            
            response = await client.get(f"{MT5_BRIDGE_URL}/bridge/account", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                account = data.get("account_info", {})
                print(f"   Account Login: {account.get('login')}")
                print(f"   Account Name: {account.get('name')}")
                print(f"   Server: {account.get('server')}")
                print(f"   Currency: {account.get('currency')}")
                print(f"   Balance: {account.get('balance')}")
                print(f"   Equity: {account.get('equity')}")
                print(f"   Trade Allowed: {account.get('trade_allowed')}")
            else:
                error_data = await response.atext()
                print(f"   Account info error: {response.status_code} - {error_data}")
                
    except Exception as e:
        print(f"Account info error: {e}")

async def test_symbols_list():
    """Test getting available symbols"""
    print(f"\n4. Testing Available Symbols...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"X-API-Key": MT5_BRIDGE_API_KEY}
            
            response = await client.get(f"{MT5_BRIDGE_URL}/bridge/symbols", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                symbols = data.get("symbols", [])
                print(f"   Total symbols available: {len(symbols)}")
                
                # Show first 10 forex symbols
                forex_symbols = [s for s in symbols if any(pair in s['name'] for pair in ['EUR', 'GBP', 'USD', 'JPY']) and len(s['name']) == 6][:10]
                if forex_symbols:
                    print(f"   First 10 Forex symbols:")
                    for symbol in forex_symbols:
                        print(f"      - {symbol['name']} - {symbol.get('description', 'N/A')}")
                else:
                    print(f"   No forex symbols found in first 50 results")
            else:
                error_data = await response.atext()
                print(f"   Symbols list error: {response.status_code} - {error_data}")
                
    except Exception as e:
        print(f"Symbols list error: {e}")

async def test_railway_backend_quotes():
    """Test the Railway backend quotes endpoint"""
    print(f"\n5. Testing Railway Backend MT5 Quotes Endpoint...")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://web-production-51f67.up.railway.app/mt5/quotes",
                params={"symbols": "EURUSD,GBPUSD,USDJPY"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Backend Status: {data.get('status')}")
                print(f"   Bridge Connected: {data.get('bridge_connected')}")
                print(f"   Last Update: {data.get('last_update')}")
                
                quotes = data.get('quotes', {})
                if quotes:
                    print(f"   Retrieved {len(quotes)} quotes:")
                    for symbol, quote in quotes.items():
                        print(f"      - {symbol}: Bid={quote.get('bid')}, Ask={quote.get('ask')}, Time={quote.get('time')}")
                else:
                    print(f"   No quotes data returned")
            else:
                print(f"   Backend quotes error: {response.status_code}")
                print(f"   Response: {await response.atext()}")
                
    except Exception as e:
        print(f"Railway backend test error: {e}")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("AI CASH REVOLUTION - MT5 INTEGRATION TEST")
    print("=" * 60)
    print(f"Bridge URL: {MT5_BRIDGE_URL}")
    print(f"API Key: {MT5_BRIDGE_API_KEY[:20]}...")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test bridge connection
    bridge_connected = await test_mt5_bridge_connection()
    
    if bridge_connected:
        # Run additional tests if bridge is connected
        await test_account_info()
        await test_symbols_list()
        await test_mt5_quotes()
    
    # Always test Railway backend regardless of bridge status
    await test_railway_backend_quotes()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())