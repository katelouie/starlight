# 🌟 Starlight

A modern Python library for astrological chart calculation and visualization, built on the Swiss Ephemeris for astronomical accuracy.

## ✨ Features

- **Accurate Calculations**: Built on Swiss Ephemeris for precise planetary positions
- **Multiple House Systems**: Placidus, Whole Sign, and more
- **Beautiful Visualizations**: SVG chart generation with customizable styling
- **Comprehensive Aspects**: Major and minor aspects with configurable orbs
- **Moon Phases**: Accurate lunar phase calculations and artistic visualizations
- **Location Support**: City name lookup with automatic coordinate resolution
- **Time Zone Handling**: Automatic UTC conversion from local times
- **Caching System**: Performance optimization for repeated calculations

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/starlight.git
cd starlight

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -e .
```

### Basic Usage

```python
from datetime import datetime
import pytz
from starlight.chart import Chart
from starlight.drawing import draw_chart

# Create a natal chart
chart = Chart(
    datetime_utc=datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC),
    loc_name="San Francisco, CA",
    houses='Placidus'
)

# Generate an SVG visualization
draw_chart(chart, "my_chart.svg", size=600)

# Access planetary positions
for planet in chart.planets:
    print(f"{planet.name}: {planet.long:.1f}° in {planet.sign}")

# Access aspects
for aspect in chart.aspects:
    print(f"{aspect.planet1.name} {aspect.aspect_name} {aspect.planet2.name} (orb: {aspect.orb:.1f}°)")
```

## 📁 Project Structure

```
starlight/
├── src/starlight/           # Core library
│   ├── chart.py             # Chart calculation and objects
│   ├── drawing.py           # SVG chart visualization
│   ├── objects.py           # Astrological objects and data
│   ├── cache.py             # Performance caching system
│   └── ...
├── docs/                    # Documentation
│   ├── planning/            # Project planning and architecture
│   └── development/         # Development guides
├── tests/                   # Testing suite
│   ├── test_chart_generation.py  # Comprehensive visual tests
│   └── output/              # Generated test files
│       ├── charts/          # Chart SVG outputs
│       └── moon_phases/     # Moon phase visualizations
├── examples/                # Usage examples
│   ├── usage.py             # Basic examples
│   └── usage_example.ipynb  # Interactive Jupyter notebook
└── data/                    # Swiss Ephemeris data files
```

## 🎯 Core Capabilities

### Chart Generation ✅
- [x] Input date, time, and location → get planetary positions
- [x] Calculate planets in signs and houses  
- [x] Generate chart angles (ASC, MC, DSC, IC)
- [x] Support multiple house systems (Placidus, Whole Sign)
- [x] City name and coordinate lookup
- [x] Local time to UTC conversion

### Planetary Information ✅
- [x] Longitude, latitude, declination
- [x] Speed and retrograde detection
- [x] Moon phase calculations
- [x] Midpoint calculations

### Aspect Analysis ✅  
- [x] Major aspects (conjunction, opposition, square, trine, sextile)
- [x] Minor aspects with configurable orbs
- [x] Applying/separating movement detection
- [x] Customizable aspect selection and orb values
- [x] Aspects with midpoints and angles

### Visualization ✅
- [x] Professional SVG chart drawing
- [x] Planet placement with collision detection
- [x] Aspect line rendering with conjunction arcs
- [x] Zodiac signs and house divisions
- [x] Moon phase artistic representation
- [x] Customizable styling and colors

## 🌙 Moon Phase Visualization

Starlight includes a sophisticated moon phase visualization system:

```python
from starlight.drawing import draw_moon_phase_standalone

# Generate individual moon phases
draw_moon_phase_standalone(0.25, True, "waxing_crescent.svg")   # 25% illuminated, waxing
draw_moon_phase_standalone(0.75, False, "waning_gibbous.svg")   # 75% illuminated, waning

# Run moon phase demo
cd tests
python test_chart_generation.py moon
```

## 📊 Output Formats

### Visual Charts
- **SVG Format**: Scalable vector graphics for web and print
- **Professional Styling**: Clean, publication-ready appearance
- **Customizable**: Colors, fonts, and layout options

### Data Tables
- **Planetary Positions**: Longitude, sign, house placement
- **Aspect Tables**: Organized by orb strength or aspect type  
- **House Cusps**: Precise cusp positions for all house systems

### Rich Console Output
Check out `examples/usage.py` for formatted output using `rich` tables.

## 🧪 Testing

### Run All Tests
```bash
cd tests
python test_chart_generation.py
```

### Individual Test Categories
```bash
cd tests
python test_chart.py        # Chart calculations
python test_objects.py      # Astrological objects  
python test_signs.py        # Zodiac sign functions
```

### Visual Test Outputs
All test outputs are organized in `tests/output/`:
- `charts/`: Complete chart visualizations
- `moon_phases/`: All 8 lunar phases

## ⚙️ Configuration

### Swiss Ephemeris Data
The `data/` directory contains Swiss Ephemeris files for astronomical calculations. Download additional data files from the [Swiss Ephemeris FTP](https://www.astro.com/swisseph/ephe/) as needed.

### House Systems
Supported house systems:
- **Placidus** (default)
- **Whole Sign**
- **Equal House**
- **Koch**
- **Campanus**

### Aspect Configuration
```python
# Customize aspect orbs
chart = Chart(
    datetime_utc=dt,
    loc_name="San Francisco, CA", 
    aspect_set="major",  # "major", "minor", "all"
    orb_set="tight"      # "tight", "normal", "wide"
)
```

## 🔮 Planned Features

### Chart Analysis (In Progress)
- [ ] Element and modality balance calculation
- [ ] Dispositor flow analysis  
- [ ] Aspect pattern detection (Grand Trine, T-Square, etc.)
- [ ] Stellium identification
- [ ] Astrological alphabet energy pairings

### Advanced Output
- [ ] Multiple house systems in single chart
- [ ] Aspect table ordering options (by orb, type, etc.)
- [ ] Triangle aspect grid format
- [ ] Interactive web charts

## 🛠️ Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Resources
- [Project Documentation](docs/) - Planning documents and architectural decisions
- [Swiss Ephemeris Documentation](https://astrorigin.com/pyswisseph/sphinx/index.html)
- [PySwissEph Programmer's Manual](https://astrorigin.com/pyswisseph/sphinx/programmers_manual/planetary_positions/position_and_speed.html)
- [Astrological Calculations](https://astrorigin.com/pyswisseph/)

## 📜 License

This project is open source. Please respect the Swiss Ephemeris license terms for astronomical data usage.

## 🙏 Acknowledgments

- **Swiss Ephemeris**: Astronomical calculation engine
- **Astro.com**: Ephemeris data and resources
- **PySwissEph**: Python bindings for Swiss Ephemeris

---

*Built with precision, designed for astrologers* ✨