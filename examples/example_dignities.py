#!/usr/bin/env python3
"""Example usage of the planetary dignities calculator."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
import pytz


def demo_dignities_calculator():
    """Demonstrate the dignities calculator with example data."""
    
    print("🌟 STARLIGHT DIGNITIES CALCULATOR DEMO 🌟")
    print("=" * 50)
    
    # The dignities calculator requires the Swiss Ephemeris data files
    # which aren't included in this demo. This example shows the API usage.
    
    print("\n📖 WHAT THE DIGNITIES CALCULATOR DOES:")
    print("-" * 40)
    print("✨ Calculates planetary essential dignities")
    print("✨ Supports traditional and modern rulership systems")
    print("✨ Includes rulership, exaltation, triplicity, bounds, and decans")
    print("✨ Accounts for day/night chart sect")
    print("✨ Provides numerical scoring system")
    
    print("\n🎯 USAGE EXAMPLE:")
    print("-" * 40)
    
    example_code = '''
from starlight.chart import Chart
from datetime import datetime
import pytz

# Create a chart
chart = Chart(
    datetime_utc=datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC),
    houses="Placidus",
    loc=(37.386051, -122.083855),  # San Francisco
    loc_name="San Francisco, CA"
)

# Get traditional dignities
traditional_dignities = chart.get_planetary_dignities(traditional=True)

# Get modern dignities  
modern_dignities = chart.get_planetary_dignities(traditional=False)

# Print dignities table
from starlight.presentation import create_table_dignities
print(create_table_dignities(chart, plain=True, traditional=True))
'''
    
    print(example_code)
    
    print("\n📊 DIGNITY SCORING SYSTEM:")
    print("-" * 40)
    print("Ruler:      +5 points")
    print("Exaltation: +4 points") 
    print("Triplicity: +3 points (cooperating ruler gets +2)")
    print("Bounds:     +2 points")
    print("Decan:      +1 point")
    print("Detriment:  -5 points")
    print("Fall:       -4 points")
    
    print("\n🔍 DIGNITY TYPES EXPLAINED:")
    print("-" * 40)
    print("• RULER: Planet rules the sign (e.g., Mars rules Aries)")
    print("• EXALTATION: Planet is exalted in the sign (e.g., Sun exalted in Aries)")
    print("• TRIPLICITY: Planet rules the element in day/night charts")
    print("• BOUNDS: Planet rules specific degrees within the sign (Egyptian system)")
    print("• DECAN: Planet rules 10° sections of the sign (Triplicity system)")
    print("• DETRIMENT: Planet opposite its ruling sign (weakened)")
    print("• FALL: Planet opposite its exaltation (weakened)")
    
    print("\n📈 SAMPLE OUTPUT:")
    print("-" * 40)
    
    sample_output = '''
Planetary Dignities (Traditional)
----------------------------------------------------------------------
Chart Sect: Day
----------------------------------------------------------------------
Planet     | Sign         | Deg    | Dignities                 | Score
----------------------------------------------------------------------
Sun        | Capricorn    |  15.2° | None                     |   0
Mars       | Scorpio      |  8.1°  | ruler                    |   5
Venus      | Sagittarius  |  22.7° | None                     |   0
Jupiter    | Libra        |  3.4°  | detriment                |  -5
Moon       | Aquarius     |  28.9° | None                     |   0
Mercury    | Capricorn    |  2.1°  | bound                    |   2
Saturn     | Aquarius     |  12.8° | ruler                    |   5

Bounds & Decan Rulers
--------------------------------------------------
Sun        | Bound: Saturn     | Decan: Saturn
Mars       | Bound: Mars       | Decan: Mars  
Venus      | Bound: Saturn     | Decan: Mercury
Jupiter    | Bound: Jupiter    | Decan: Saturn
Moon       | Bound: Venus      | Decan: Mercury
Mercury    | Bound: Mercury    | Decan: Saturn
Saturn     | Bound: Venus      | Decan: Mercury
'''
    
    print(sample_output)
    
    print("\n🔮 INTERPRETATION TIPS:")
    print("-" * 40)
    print("• High positive scores = planet is strong and well-placed")
    print("• Negative scores = planet is challenged or weakened")
    print("• Score of 0 = planet is in a neutral position")
    print("• Consider both traditional and modern systems")
    print("• Day/night sect affects triplicity rulerships")
    
    print("\n🚀 TO RUN WITH REAL DATA:")
    print("-" * 40)
    print("1. Download Swiss Ephemeris data files")
    print("2. Place them in src/starlight/data/swisseph/ephe/")
    print("3. Run the full chart calculation")
    print("4. Use the presentation module for formatted output")
    
    print("\n✨ Happy calculating! ✨")


if __name__ == "__main__":
    demo_dignities_calculator()