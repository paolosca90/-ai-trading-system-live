#!/usr/bin/env python3
"""
Complete Production System Test
Tests all key components of the AI Cash-Revolution system
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "https://web-production-51f67.up.railway.app"

async def test_system_health():
    """Test basic system health"""
    print("1. Testing System Health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backend healthy: {data.get('status')}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

async def test_mt5_quotes():
    """Test real MT5 quotes endpoint"""
    print("\n2. Testing Real MT5 Quotes...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{BASE_URL}/api/mt5/quotes-public?symbols=EURUSD,GBPUSD,XAUUSD,US500")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('quotes'):
                    quotes = data['quotes']
                    print(f"   ✅ MT5 Bridge connected: {data.get('bridge_connected')}")
                    print(f"   📊 Retrieved {len(quotes)} real quotes:")
                    for symbol, quote in quotes.items():
                        print(f"      • {symbol}: {quote.get('bid', quote.get('close', 'N/A'))}")
                    return True
                else:
                    print(f"   ⚠️ MT5 quotes issue: {data.get('message')}")
                    return False
            else:
                print(f"   ❌ Quotes endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Quotes test error: {e}")
        return False

async def test_signal_generation():
    """Test automatic signal generation"""
    print("\n3. Testing AI Signal Generation...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BASE_URL}/api/generate-signals-auto")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Generation status: {data.get('status')}")
                print(f"   🤖 Message: {data.get('message')}")
                
                if data.get('signals_generated', 0) > 0:
                    print(f"   📈 Generated {data['signals_generated']} new signals")
                
                return True
            else:
                print(f"   ❌ Signal generation failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Signal generation error: {e}")
        return False

async def test_signals_endpoint():
    """Test signals retrieval"""
    print("\n4. Testing Signals Retrieval...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{BASE_URL}/signals/top")
            
            if response.status_code == 200:
                data = response.json()
                signals = data.get('signals', [])
                print(f"   ✅ Retrieved {len(signals)} signals from database")
                
                if signals:
                    print("   📊 Sample signals:")
                    for i, signal in enumerate(signals[:3]):
                        symbol = signal.get('asset', 'Unknown')
                        signal_type = signal.get('signal_type', 'Unknown')
                        confidence = signal.get('reliability', 0)
                        print(f"      • Signal {i+1}: {signal_type} {symbol} ({confidence}% confidence)")
                
                return len(signals) > 0
            else:
                print(f"   ❌ Signals endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Signals test error: {e}")
        return False

async def test_dashboard_pages():
    """Test main dashboard pages"""
    print("\n5. Testing Frontend Pages...")
    pages = [
        ("Dashboard", "/dashboard.html"),
        ("Signals", "/signals.html"), 
        ("Profile", "/profile.html"),
        ("MT5 Integration", "/mt5-integration.html")
    ]
    
    results = []
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, path in pages:
                response = await client.get(f"{BASE_URL}{path}")
                if response.status_code == 200:
                    print(f"   ✅ {name} page loads correctly")
                    results.append(True)
                else:
                    print(f"   ❌ {name} page failed: {response.status_code}")
                    results.append(False)
        
        return all(results)
    except Exception as e:
        print(f"   ❌ Frontend test error: {e}")
        return False

async def main():
    """Run complete system test"""
    print("=" * 70)
    print("🚀 AI CASH-REVOLUTION PRODUCTION SYSTEM TEST")
    print("=" * 70)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("System Health", test_system_health),
        ("MT5 Real Quotes", test_mt5_quotes),
        ("AI Signal Generation", test_signal_generation),
        ("Signals Database", test_signals_endpoint),
        ("Frontend Pages", test_dashboard_pages)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-" * 70)
    print(f"🎯 Overall Score: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL - PRODUCTION READY!")
    elif passed >= total * 0.8:
        print("⚠️ MOSTLY OPERATIONAL - Minor issues detected")
    else:
        print("🚨 CRITICAL ISSUES - System needs attention")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)