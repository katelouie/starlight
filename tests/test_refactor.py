#!/usr/bin/env python3
"""Test the refactored code."""

import sys
sys.path.insert(0, 'src')

try:
    from starlight.chart import Chart
    from starlight.presentation import create_table_planets, create_table_sect
    
    # Test basic functionality
    chart = Chart(
        date={'year': 1994, 'month': 1, 'day': 6, 'hour': 19, 'minute': 47},
        loc=(37.386051, -122.083855),
        houses='Placidus'
    )
    
    # Test the chart methods
    sect = chart.get_sect()
    print(f"Chart sect: {sect}")
    
    # Test planet house calculation
    if chart.planets:
        planet = chart.planets[0]
        house = chart.get_planet_house(planet)
        print(f"{planet.name} is in house {house}")
    
    # Test aspects
    aspects = chart.get_all_aspects()
    print(f"Found {len(aspects)} aspects")
    
    # Test presentation function
    result = create_table_planets(chart, plain=True)
    print("\nPlanet table created successfully")
    
    # Test sect presentation
    sect_result = create_table_sect(chart, plain=True)
    print(f"Sect presentation: {sect_result}")
    
    print("\nSUCCESS: Method-based refactoring works!")
    print(f"Chart has {len(chart.planets)} planets")
    print(f"Chart has {len(chart.angles)} angles")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()