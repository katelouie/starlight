# Starlight Tests

This directory contains all test files and test outputs for the Starlight astrology library.

## Directory Structure

```
tests/
├── README.md                     # This file
├── test_chart_generation.py      # Comprehensive chart generation tests
├── test_*.py                     # Individual component tests
└── output/                       # Test output files
    ├── charts/                   # Chart SVG outputs
    │   ├── test_basic_wheel.svg
    │   ├── test_planets.svg
    │   ├── test_collision.svg
    │   ├── test_aspects.svg
    │   ├── test_conjunctions.svg
    │   ├── test_moon_in_chart.svg
    │   └── test_real_chart.svg
    └── moon_phases/              # Moon phase SVG outputs
        ├── new_moon.svg
        ├── waxing_crescent.svg
        ├── first_quarter.svg
        ├── waxing_gibbous.svg
        ├── full_moon.svg
        ├── waning_gibbous.svg
        ├── third_quarter.svg
        └── waning_crescent.svg
```

## Running Tests

### Full Test Suite
```bash
cd tests
python test_chart_generation.py
```

### Moon Phase Demo Only
```bash
cd tests
python test_chart_generation.py moon
```

### Individual Tests
```bash
cd tests
python test_chart.py        # Chart object tests
python test_objects.py      # Astrological object tests
python test_signs.py        # Zodiac sign tests
```

## Test Outputs

All test outputs are organized in the `output/` directory:

- **charts/**: Complete astrological chart visualizations testing different aspects of the drawing system
- **moon_phases/**: Individual moon phase visualizations showing all 8 major phases

Open any SVG file in a web browser to view the visual results.

## Adding New Tests

When adding new tests that generate visual outputs:

1. Use the `CHART_OUTPUT_DIR` for chart-related SVGs
2. Use the `MOON_OUTPUT_DIR` for moon phase SVGs  
3. Create new subdirectories in `output/` for other types of visual tests
4. Update this README to document the new test structure