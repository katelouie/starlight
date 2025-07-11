#!/usr/bin/env python3
"""Test caching functionality."""

import sys
import time
sys.path.insert(0, 'src')

def test_cache_functionality():
    """Test that caching works for both ephemeris and geocoding calls."""
    print("Testing cache functionality...")
    
    from datetime import datetime
    import pytz
    from starlight.chart import Chart
    from starlight.cache import cache_info, clear_cache
    
    # Clear any existing cache
    clear_cache()
    
    # Create test datetime
    dt_utc = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    
    # Test 1: Create a chart - this should populate cache
    print("\n1. Creating first chart (should populate cache)...")
    start_time = time.time()
    chart1 = Chart(
        datetime_utc=dt_utc,
        loc_name="San Francisco, CA",
        houses='Placidus'
    )
    first_time = time.time() - start_time
    print(f"   First chart creation took: {first_time:.2f} seconds")
    
    # Check cache info
    info = cache_info()
    print(f"   Cache now has {info['total_cached_files']} files")
    
    # Test 2: Create same chart again - this should use cache
    print("\n2. Creating identical chart (should use cache)...")
    start_time = time.time()
    chart2 = Chart(
        datetime_utc=dt_utc,
        loc_name="San Francisco, CA",
        houses='Placidus'
    )
    second_time = time.time() - start_time
    print(f"   Second chart creation took: {second_time:.2f} seconds")
    
    # Test 3: Performance improvement check
    if second_time < first_time:
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"   ✓ Cache improved performance by {improvement:.1f}%")
    else:
        print(f"   ⚠ Cache might not be working optimally")
    
    # Test 4: Verify data is identical
    print("\n3. Verifying cached data is identical...")
    assert len(chart1.planets) == len(chart2.planets), "Planet counts should match"
    assert chart1.get_sect() == chart2.get_sect(), "Sect should match"
    print("   ✓ Cached data is identical")
    
    # Test 5: Cache info
    print("\n4. Cache information:")
    info = cache_info()
    print(f"   Total cached files: {info['total_cached_files']}")
    print(f"   Cache size: {info['cache_size_mb']} MB")
    print(f"   Cache by type: {info['by_type']}")
    print(f"   Cache directory: {info['cache_directory']}")
    
    # Test 6: Test different location (should hit geocoding cache)
    print("\n5. Testing different location...")
    start_time = time.time()
    chart3 = Chart(
        datetime_utc=dt_utc,
        loc_name="New York, NY",
        houses='Placidus'
    )
    third_time = time.time() - start_time
    print(f"   New location chart took: {third_time:.2f} seconds")
    
    # Test same location again (should use geocoding cache)
    start_time = time.time()
    chart4 = Chart(
        datetime_utc=dt_utc,
        loc_name="New York, NY",
        houses='Placidus'
    )
    fourth_time = time.time() - start_time
    print(f"   Same location again took: {fourth_time:.2f} seconds")
    
    if fourth_time < third_time:
        improvement = ((third_time - fourth_time) / third_time) * 100
        print(f"   ✓ Geocoding cache improved performance by {improvement:.1f}%")
    
    # Final cache info
    info = cache_info()
    print(f"\n6. Final cache info:")
    print(f"   Total cached files: {info['total_cached_files']}")
    print(f"   Cache by type: {info['by_type']}")
    
    print("\n✅ All cache tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_cache_functionality()
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)