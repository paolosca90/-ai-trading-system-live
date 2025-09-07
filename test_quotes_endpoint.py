#!/usr/bin/env python3
"""
Test the new public quotes endpoint
"""

import httpx
import asyncio
import json
from datetime import datetime

async def test_public_quotes_endpoint():
    """Test the new public quotes endpoint"""
    print("Testing public quotes endpoint...")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Test with specific symbols
            response = await client.get(
                "https://web-production-51f67.up.railway.app/api/mt5/quotes-public",
                params={"symbols": "EURUSD,GBPUSD,USDJPY,AUDUSD"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status')}")
                print(f"Bridge Connected: {data.get('bridge_connected')}")
                print(f"Last Update: {data.get('last_update')}")
                
                quotes = data.get('quotes', {})
                print(f"\nRetrieved {len(quotes)} quotes:")
                for symbol, quote in quotes.items():
                    print(f"  {symbol}: Bid={quote.get('bid')}, Ask={quote.get('ask')}, Time={quote.get('time')}")
                
                return True
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    """Run the test"""
    print("=" * 50)
    print("PUBLIC QUOTES ENDPOINT TEST")
    print("=" * 50)
    
    success = await test_public_quotes_endpoint()
    
    print("\n" + "=" * 50)
    print(f"TEST {'PASSED' if success else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())