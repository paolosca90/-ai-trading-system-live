#!/usr/bin/env python3
"""
Test script per verificare gli endpoint VPS API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your Railway URL when deployed
VPS_API_KEY = "1d2376ae63aedb38f4d13e1041fb5f0b56cc48c44a8f106194d2da23e4039736"

HEADERS = {
    "Content-Type": "application/json",
    "X-VPS-API-Key": VPS_API_KEY
}

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_vps_heartbeat():
    """Test VPS heartbeat endpoint"""
    print("\n💚 Testing VPS heartbeat...")
    
    heartbeat_data = {
        "vps_id": "vps-test-001",
        "status": "active",
        "signals_generated": 15,
        "errors_count": 2,
        "uptime_seconds": 86400,
        "version": "1.0.0",
        "mt5_status": "connected"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/vps/heartbeat",
            json=heartbeat_data,
            headers=HEADERS
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_signal_receive():
    """Test signal receive endpoint"""
    print("\n📊 Testing signal receive...")
    
    signal_data = {
        "vps_id": "vps-test-001",
        "generated_at": datetime.now().isoformat(),
        "reliability": 85.5,
        "ai_analysis": "Strong bullish momentum detected. RSI oversold, MACD turning positive. Recommended entry at current levels.",
        "confidence_score": 87.2,
        "signal": {
            "symbol": "EURUSD",
            "signal_type": "BUY",
            "entry_price": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0950,
            "reliability": 85.5,
            "risk_level": "MEDIUM"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/signals/receive",
            json=signal_data,
            headers=HEADERS
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_latest_signals():
    """Test latest signals endpoint"""
    print("\n📈 Testing latest signals...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/signals/latest?limit=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_vps_status():
    """Test VPS status endpoint"""
    print("\n🖥️ Testing VPS status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/vps/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_api_key():
    """Test API key validation"""
    print("\n🔐 Testing API key validation...")
    
    invalid_headers = {
        "Content-Type": "application/json",
        "X-VPS-API-Key": "invalid-key"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/vps/heartbeat",
            json={"vps_id": "test", "status": "active"},
            headers=invalid_headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 401  # Should be unauthorized
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VPS API ENDPOINTS TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("VPS Heartbeat", test_vps_heartbeat),
        ("Signal Receive", test_signal_receive),
        ("Latest Signals", test_latest_signals),
        ("VPS Status", test_vps_status),
        ("Invalid API Key", test_invalid_api_key)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY RESULTS:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:8} {test_name}")
    
    print(f"\n🎯 TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VPS API endpoints are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)