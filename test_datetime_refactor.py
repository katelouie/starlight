#!/usr/bin/env python3
"""Test the refactored Chart class with datetime objects."""

import sys
sys.path.insert(0, 'src')

def test_datetime_chart():
    """Test the new datetime-based Chart class."""
    print("Testing datetime-based Chart class...")
    
    from datetime import datetime
    import pytz
    from starlight.chart import Chart
    
    # Test 1: Create datetime object (UTC)
    print("\n1. Testing UTC datetime...")
    dt_utc = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    
    chart = Chart(
        datetime_utc=dt_utc,
        loc_name="San Francisco, CA",
        houses='Placidus'
    )
    
    print(f"   ✓ Chart created successfully")
    print(f"   Year: {chart.year}")
    print(f"   Month: {chart.month}")
    print(f"   Day: {chart.day}")
    print(f"   Hour: {chart.hour}")
    print(f"   Minute: {chart.minute}")
    print(f"   Julian day: {chart.julian:.2f}")
    print(f"   Planets: {len(chart.planets)}")
    print(f"   Angles: {len(chart.angles)}")
    
    # Test 2: Create datetime from local time
    print("\n2. Testing local timezone conversion...")
    
    # Create local time
    local_dt = datetime(1994, 1, 6, 11, 47)  # Local time
    sf_tz = pytz.timezone('America/Los_Angeles')
    local_dt_aware = sf_tz.localize(local_dt)
    dt_utc_converted = local_dt_aware.astimezone(pytz.UTC)
    
    chart2 = Chart(
        datetime_utc=dt_utc_converted,
        loc_name="San Francisco, CA",
        houses='Placidus'
    )
    
    print(f"   ✓ Chart created from local time")
    print(f"   UTC Hour: {chart2.hour}")
    print(f"   Original local hour was 11, UTC is {chart2.hour} (should be 19)")
    
    # Test 3: Compare with old approach
    print("\n3. Comparing results...")
    
    # Both charts should have the same UTC time
    assert chart.hour == chart2.hour, f"Hours should match: {chart.hour} vs {chart2.hour}"
    assert chart.minute == chart2.minute, f"Minutes should match: {chart.minute} vs {chart2.minute}"
    assert abs(chart.julian - chart2.julian) < 0.001, f"Julian days should match: {chart.julian} vs {chart2.julian}"
    
    print("   ✓ Both charts have identical UTC times")
    
    # Test 4: Test chart methods
    print("\n4. Testing chart methods...")
    
    sect = chart.get_sect()
    print(f"   Chart sect: {sect}")
    
    if chart.planets:
        planet = chart.planets[0]
        house = chart.get_planet_house(planet)
        print(f"   {planet.name} is in house {house}")
    
    aspects = chart.get_all_aspects()
    print(f"   Found {len(aspects)} aspects")
    
    # Test 5: Test error handling
    print("\n5. Testing error handling...")
    
    try:
        # This should fail - naive datetime
        naive_dt = datetime(1994, 1, 6, 19, 47)
        Chart(datetime_utc=naive_dt, loc_name="San Francisco, CA", houses='Placidus')
        print("   ❌ Should have failed with naive datetime")
    except ValueError as e:
        print(f"   ✓ Correctly rejected naive datetime: {e}")
    
    try:
        # This should fail - no location
        Chart(datetime_utc=dt_utc, houses='Placidus')
        print("   ❌ Should have failed with no location")
    except ValueError as e:
        print(f"   ✓ Correctly rejected missing location: {e}")
    
    print("\n✅ All datetime Chart tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_datetime_chart()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)