#!/usr/bin/env python3
"""Test the method-based Chart API."""

import sys
sys.path.insert(0, 'src')

def test_chart_methods():
    """Test that the Chart class methods work properly."""
    print("Testing Chart class methods...")
    
    # Test method existence
    from starlight.chart import Chart
    
    # Create a chart instance
    chart = Chart(
        date={'year': 1994, 'month': 1, 'day': 6, 'hour': 19, 'minute': 47},
        loc=(37.386051, -122.083855),
        houses='Placidus'
    )
    
    # Test method existence
    assert hasattr(chart, 'get_sect'), "Chart should have get_sect method"
    assert hasattr(chart, 'get_planet_house'), "Chart should have get_planet_house method"
    assert hasattr(chart, 'get_all_aspects'), "Chart should have get_all_aspects method"
    assert hasattr(chart, 'get_planetary_dignities'), "Chart should have get_planetary_dignities method"
    assert hasattr(chart, 'get_midpoint_aspects'), "Chart should have get_midpoint_aspects method"
    
    # Test method functionality
    sect = chart.get_sect()
    assert sect in ['Day', 'Night'], f"Sect should be 'Day' or 'Night', got: {sect}"
    print(f"✓ Chart sect: {sect}")
    
    if chart.planets:
        planet = chart.planets[0]
        house = chart.get_planet_house(planet)
        assert 1 <= house <= 12, f"House should be 1-12, got: {house}"
        print(f"✓ {planet.name} is in house {house}")
    
    aspects = chart.get_all_aspects()
    assert isinstance(aspects, list), "get_all_aspects should return a list"
    print(f"✓ Found {len(aspects)} aspects")
    
    dignities = chart.get_planetary_dignities()
    assert isinstance(dignities, dict), "get_planetary_dignities should return a dict"
    print(f"✓ Calculated dignities for {len(dignities)} planets")
    
    midpoint_aspects = chart.get_midpoint_aspects()
    assert isinstance(midpoint_aspects, list), "get_midpoint_aspects should return a list"
    print(f"✓ Found {len(midpoint_aspects)} midpoint aspects")
    
    print("\n✅ All method tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_chart_methods()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)