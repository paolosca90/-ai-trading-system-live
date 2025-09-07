#!/usr/bin/env python3
"""
Test the date calculation fix
"""

from datetime import datetime, timezone

def safe_date_diff_days(end_date, start_date=None):
    """
    Safely calculate difference in days between two dates, handling timezone issues
    """
    if not end_date:
        return 0
        
    if start_date is None:
        start_date = datetime.utcnow()
    
    try:
        # Handle timezone-aware and naive datetime comparison
        if end_date.tzinfo is not None:
            # end_date is timezone-aware
            if start_date.tzinfo is None:
                from datetime import timezone
                start_date = start_date.replace(tzinfo=timezone.utc)
        else:
            # end_date is naive
            if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
                start_date = start_date.replace(tzinfo=None)
        
        return max(0, (end_date - start_date).days)
    except Exception as e:
        print(f"Date calculation error: {e}")
        return 0

# Test cases
print("Testing date calculation fix...")

# Test 1: Both naive datetimes
naive_end = datetime(2025, 12, 31, 23, 59, 59)
naive_start = datetime.utcnow()
result1 = safe_date_diff_days(naive_end, naive_start)
print(f"Test 1 (both naive): {result1} days")

# Test 2: end_date timezone-aware, start_date naive
aware_end = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
naive_start = datetime.utcnow()
result2 = safe_date_diff_days(aware_end, naive_start)
print(f"Test 2 (end aware, start naive): {result2} days")

# Test 3: Both timezone-aware
aware_end = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
aware_start = datetime.utcnow().replace(tzinfo=timezone.utc)
result3 = safe_date_diff_days(aware_end, aware_start)
print(f"Test 3 (both aware): {result3} days")

# Test 4: None end_date
result4 = safe_date_diff_days(None)
print(f"Test 4 (None end_date): {result4} days")

print("All tests passed!")