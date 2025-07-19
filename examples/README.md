# Starlight Examples

This directory contains example scripts showing how to use the Starlight astrology library.

## Basic Usage Examples

### Creating Charts
```python
from datetime import datetime
import pytz
from starlight.chart import Chart
from starlight.drawing_new import draw_chart

# Create a chart for a specific date/time/location
dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
chart = Chart(
    datetime_utc=dt,
    loc_name="San Francisco, CA",
    houses='Placidus'
)

# Draw the chart as an SVG
draw_chart(chart, "my_chart.svg", size=600)
```

### Moon Phase Visualization
```python
from starlight.drawing_new import draw_moon_phase_standalone

# Create individual moon phase visualizations
draw_moon_phase_standalone(0.25, True, "waxing_crescent.svg")   # 25% illuminated, waxing
draw_moon_phase_standalone(0.75, False, "waning_gibbous.svg")   # 75% illuminated, waning
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