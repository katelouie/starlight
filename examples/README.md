# Starlight Examples

This directory contains example scripts showing how to use the Starlight astrology library.

## Basic Usage Examples

### Creating Charts
```python
from datetime import datetime
import pytz
from starlight.chart import Chart
from starlight.drawing import draw_chart

# Create a chart for a specific date/time/location
dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
chart = Chart(
    datetime_utc=dt,
    loc_name="San Francisco, CA",
    houses='Koch'  # Try different house systems: Placidus, Whole Sign, Equal, etc.
)

# Draw the chart as an SVG
draw_chart(chart, "my_chart.svg", size=600)

# Access planetary positions
for planet in chart.planets:
    print(f"{planet.name}: {planet.long:.1f}° in {planet.sign}")

# Access Arabic Parts
for part in chart.arabic_parts:
    print(f"{part.name}: {part.long:.1f}° in {part.sign}")
```

### Moon Phase Visualization
```python
from starlight.drawing import draw_moon_phase_standalone

# Create individual moon phase visualizations
draw_moon_phase_standalone(0.25, True, "waxing_crescent.svg")   # 25% illuminated, waxing
draw_moon_phase_standalone(0.75, False, "waning_gibbous.svg")   # 75% illuminated, waning
```

### House Systems
```python
# Starlight supports 23+ house systems
house_systems = [
    "Placidus", "Koch", "Porphyry", "Regiomontanus", "Campanus",
    "Whole Sign", "Equal", "Vehlow Equal", "Alcabitius", "Topocentric"
]

for system in house_systems[:3]:  # Try first 3
    chart = Chart(datetime_utc=dt, loc_name="New York, NY", houses=system)
    print(f"\n{system} Houses:")
    for i, cusp in enumerate(chart.cusps[:3], 1):
        print(f"  House {i}: {cusp:.1f}°")
```

### Arabic Parts Analysis
```python
# Analyze Arabic Parts for relationship insights
relationship_parts = [
    "Part of Fortune", "Part of Spirit", "Part of Love", 
    "Part of Marriage", "Part of Eros"
]

for part in chart.arabic_parts:
    if part.name in relationship_parts:
        print(f"{part.name}: {part.long:.1f}° {part.sign} in House {part.house}")
```

## File Structure

- **usage.py**: Basic chart creation example
- **usage_example.ipynb**: Jupyter notebook with interactive examples
- **example_dignities.py**: Example using the dignities system

## Running Examples

```bash
cd examples
python usage.py
```

Or open the Jupyter notebook:
```bash
jupyter notebook usage_example.ipynb
```