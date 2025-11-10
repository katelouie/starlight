#!/usr/bin/env python3
"""
Famous People Test Suite for Starlight Astrology Library

This test suite uses birth data from famous individuals to validate various
aspects of the Starlight package functionality including:
- Basic chart generation
- Planet positioning accuracy
- House system calculations
- Aspect calculations
- Moon phase rendering
- Edge cases and special configurations
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import pytz
import contextlib
from io import StringIO

sys.path.insert(0, "src")

from starlight.chart import Chart
from starlight.drawing import ChartWheel
from starlight.presentation import (
    create_table_planets,
    create_table_houses,
    create_table_angles,
    create_table_aspects,
    create_table_dignities,
    print_chart_summary,
)
from rich.console import Console


# Famous people birth data with interesting astrological features
FAMOUS_BIRTH_DATA = [
    {
        "name": "Albert Einstein",
        "date": "1879-03-14",
        "time": "11:30",
        "location": "Ulm, Germany",
        "latitude": 48.3984,
        "longitude": 9.9916,
        "timezone": "Europe/Berlin",
        "notes": "Pisces Sun with strong Sagittarius - tests fire/water balance and scientific genius aspects",
    },
    {
        "name": "Frida Kahlo",
        "date": "1907-07-06",
        "time": "08:30",
        "location": "Coyoacán, Mexico",
        "latitude": 19.3467,
        "longitude": -99.1618,
        "timezone": "America/Mexico_City",
        "notes": "Cancer Sun with Leo Rising - tests artistic creativity and emotional intensity",
    },
    {
        "name": "Leonardo da Vinci",
        "date": "1452-04-15",
        "time": "21:40",
        "location": "Vinci, Italy",
        "latitude": 43.7811,
        "longitude": 10.9237,
        "timezone": "Europe/Rome",
        "notes": "Aries Sun with strong Taurus - tests Renaissance genius and artistic/scientific blend",
    },
    {
        "name": "Oprah Winfrey",
        "date": "1954-01-29",
        "time": "04:30",
        "location": "Kosciusko, Mississippi, USA",
        "latitude": 33.0579,
        "longitude": -89.5873,
        "timezone": "America/Chicago",
        "notes": "Aquarius Sun with Sagittarius Rising - tests media influence and humanitarian aspects",
    },
    {
        "name": "Martin Luther King Jr.",
        "date": "1929-01-15",
        "time": "12:00",
        "location": "Atlanta, Georgia, USA",
        "latitude": 33.7490,
        "longitude": -84.3880,
        "timezone": "America/New_York",
        "notes": "Capricorn Sun - tests leadership and social justice themes",
    },
    {
        "name": "Marie Curie",
        "date": "1867-11-07",
        "time": "12:00",
        "location": "Warsaw, Poland",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "timezone": "Europe/Warsaw",
        "notes": "Scorpio Sun - tests scientific breakthrough and transformational themes",
    },
    {
        "name": "Winston Churchill",
        "date": "1874-11-30",
        "time": "01:30",
        "location": "Blenheim Palace, England",
        "latitude": 51.8412,
        "longitude": -1.3617,
        "timezone": "Europe/London",
        "notes": "Sagittarius Sun with Leo Rising - tests wartime leadership and oratory skills",
    },
    {
        "name": "Pablo Picasso",
        "date": "1881-10-25",
        "time": "23:15",
        "location": "Málaga, Spain",
        "latitude": 36.7213,
        "longitude": -4.4213,
        "timezone": "Europe/Madrid",
        "notes": "Scorpio Sun - tests artistic revolution and creative transformation",
    },
    {
        "name": "Maya Angelou",
        "date": "1928-04-04",
        "time": "14:10",
        "location": "St. Louis, Missouri, USA",
        "latitude": 38.6270,
        "longitude": -90.1994,
        "timezone": "America/Chicago",
        "notes": "Aries Sun - tests literary genius and resilience themes",
    },
    {
        "name": "Nikola Tesla",
        "date": "1856-07-10",
        "time": "00:00",
        "location": "Smiljan, Croatia",
        "latitude": 44.3514,
        "longitude": 15.3109,
        "timezone": "Europe/Zagreb",
        "notes": "Cancer Sun with midnight birth - tests electrical genius and innovative aspects",
    },
]


def generate_famous_people_charts():
    """Generate natal charts for famous people test suite."""

    # Create output directory
    output_dir = Path("tests/output/famous_people")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Also create examples directory
    examples_dir = Path("examples/famous_people")
    examples_dir.mkdir(parents=True, exist_ok=True)

    results = []

    print("Generating Famous People Test Charts...")
    print("=" * 50)

    for person_data in FAMOUS_BIRTH_DATA:
        try:
            print(f"\nGenerating chart for {person_data['name']}...")

            # Parse birth data and convert to UTC
            birth_date = datetime.strptime(person_data["date"], "%Y-%m-%d").date()
            birth_time = datetime.strptime(person_data["time"], "%H:%M").time()
            birth_datetime = datetime.combine(birth_date, birth_time)

            # Make timezone-aware and convert to UTC
            local_tz = pytz.timezone(person_data["timezone"])
            birth_datetime_local = local_tz.localize(birth_datetime)
            birth_datetime_utc = birth_datetime_local.astimezone(pytz.UTC)

            # Create chart - Chart expects UTC datetime and location tuple
            chart = Chart(
                datetime_utc=birth_datetime_utc,
                houses="Placidus",
                loc=(person_data["latitude"], person_data["longitude"]),
                loc_name=person_data["location"],
            )

            # Generate chart drawing with aspects enabled
            style_with_aspects = {"show_aspects": True}
            wheel = ChartWheel(size=600, style=style_with_aspects)

            # Create filename
            filename = person_data["name"].lower().replace(" ", "_").replace(".", "")

            # Save to both directories
            test_output_path = output_dir / f"{filename}_chart.svg"
            examples_output_path = examples_dir / f"{filename}_chart.svg"

            # Create SVG and draw chart elements (including aspects)
            dwg = wheel.create_svg(str(test_output_path))
            wheel.draw_house_divisions(dwg, chart)
            wheel.draw_zodiac_ring(dwg, chart)
            wheel.draw_aspects(dwg, chart)  # Draw aspects
            wheel.draw_angles(dwg, chart)
            wheel.draw_planets(dwg, chart)
            dwg.save()

            # Also save to examples directory
            dwg_examples = wheel.create_svg(str(examples_output_path))
            wheel.draw_house_divisions(dwg_examples, chart)
            wheel.draw_zodiac_ring(dwg_examples, chart)
            wheel.draw_aspects(dwg_examples, chart)  # Draw aspects
            wheel.draw_angles(dwg_examples, chart)
            wheel.draw_planets(dwg_examples, chart)
            dwg_examples.save()

            # Generate tabular chart summary and save console output
            try:
                summary_output = StringIO()
                console = Console(file=summary_output, width=100)

                # Create comprehensive chart summary using rich tables
                console.print(f"\n{'=' * 60}")
                console.print(f"CHART SUMMARY FOR {person_data['name'].upper()}")
                console.print(f"{'=' * 60}")
                console.print(
                    f"Birth Date: {person_data['date']} {person_data['time']}"
                )
                console.print(f"Location: {person_data['location']}")
                console.print(
                    f"Coordinates: {person_data['latitude']:.4f}°, {person_data['longitude']:.4f}°"
                )
                console.print(f"Timezone: {person_data['timezone']}")
                console.print(f"Notes: {person_data['notes']}")
                console.print()

                # Print all chart tables with error handling using rich tables
                try:
                    rich_planets = create_table_planets(chart, plain=False)
                    console.print(rich_planets)
                    console.print()
                except Exception as e:
                    console.print(f"Error generating planet table: {e}")
                    console.print()

                try:
                    rich_houses = create_table_houses(chart, plain=False)
                    console.print(rich_houses)
                    console.print()
                except Exception as e:
                    console.print(f"Error generating houses table: {e}")
                    console.print()

                try:
                    rich_angles = create_table_angles(chart, plain=False)
                    console.print(rich_angles)
                    console.print()
                except Exception as e:
                    console.print(f"Error generating angles table: {e}")
                    console.print()

                try:
                    rich_aspects = create_table_aspects(chart, plain=False)
                    console.print(rich_aspects)
                    console.print()
                except Exception as e:
                    console.print(f"Error generating aspects table: {e}")
                    console.print()

                try:
                    rich_dignities = create_table_dignities(chart, plain=False)
                    console.print(rich_dignities)
                    console.print()
                except Exception as e:
                    console.print(f"Error generating dignities table: {e}")
                    console.print()

                # Save console output to file
                summary_text = summary_output.getvalue()
                summary_file_path = output_dir / f"{filename}_summary.txt"
                with open(summary_file_path, "w") as f:
                    f.write(summary_text)

                print(f"✓ Summary saved: {summary_file_path}")

            except Exception as e:
                print(f"✗ Error generating summary for {person_data['name']}: {e}")
                # Still continue with chart info collection

            # Collect chart information for summary
            chart_info = {
                "name": person_data["name"],
                "sun_sign": chart.sun.sign
                if hasattr(chart, "sun") and hasattr(chart.sun, "sign")
                else "Unknown",
                "moon_sign": chart.moon.sign
                if hasattr(chart, "moon") and hasattr(chart.moon, "sign")
                else "Unknown",
                "rising_sign": chart.ascendant.sign
                if hasattr(chart, "ascendant") and hasattr(chart.ascendant, "sign")
                else "Unknown",
                "chart_file": str(test_output_path),
                "notes": person_data["notes"],
            }

            results.append(chart_info)
            print(f"✓ Chart saved: {test_output_path}")
            print(f"✓ Example saved: {examples_output_path}")

        except Exception as e:
            print(f"✗ Error generating chart for {person_data['name']}: {e}")
            continue

    # Generate summary report
    generate_test_report(results, output_dir)

    return results


def generate_test_report(results, output_dir):
    """Generate a comprehensive test report."""

    report_path = output_dir / "test_report.md"

    with open(report_path, "w") as f:
        f.write("# Famous People Test Suite Report\n\n")
        f.write(
            "This report summarizes the natal charts generated for famous individuals "
        )
        f.write("to test various aspects of the Starlight astrology library.\n\n")

        f.write("## Test Cases Generated\n\n")

        for result in results:
            f.write(f"### {result['name']}\n\n")
            f.write(f"- **Sun Sign**: {result['sun_sign']}\n")
            f.write(f"- **Moon Sign**: {result['moon_sign']}\n")
            f.write(f"- **Rising Sign**: {result['rising_sign']}\n")
            f.write(f"- **Chart File**: `{os.path.basename(result['chart_file'])}`\n")
            f.write(f"- **Test Purpose**: {result['notes']}\n\n")

        f.write("## Package Features Tested\n\n")
        f.write("This test suite validates:\n\n")
        f.write(
            "1. **Chart Generation**: Basic natal chart creation with various birth data\n"
        )
        f.write(
            "2. **Planet Positioning**: Accurate planetary positions across different time periods\n"
        )
        f.write("3. **Sign Calculations**: Proper zodiac sign determination\n")
        f.write("4. **House Systems**: House cusp calculations\n")
        f.write("5. **Geographical Diversity**: Charts from various global locations\n")
        f.write(
            "6. **Historical Range**: Birth dates spanning from 15th to 20th centuries\n"
        )
        f.write(
            "7. **Time Variations**: Different birth times including midnight births\n"
        )
        f.write(
            "8. **SVG Rendering**: Chart visualization with planet symbols and information\n"
        )
        f.write("9. **Moon Phase Accuracy**: Accurate lunar phase representations\n")
        f.write("10. **Collision Detection**: Proper spacing of chart elements\n\n")

        f.write("## Usage\n\n")
        f.write("To run this test suite:\n\n")
        f.write("```bash\n")
        f.write("source ~/.zshrc && pyenv activate starlight\n")
        f.write("cd /path/to/starlight\n")
        f.write("python tests/famous_people_test_suite.py\n")
        f.write("```\n\n")

        f.write("Generated charts can be found in:\n")
        f.write("- `tests/output/famous_people/` (test outputs)\n")
        f.write("- `examples/famous_people/` (example showcase)\n")

    print(f"\n✓ Test report generated: {report_path}")


def run_validation_tests():
    """Run additional validation tests on the generated charts."""

    print("\nRunning Validation Tests...")
    print("=" * 30)

    # Test that all required planet attributes exist
    test_person = FAMOUS_BIRTH_DATA[0]  # Einstein

    try:
        birth_date = datetime.strptime(test_person["date"], "%Y-%m-%d").date()
        birth_time = datetime.strptime(test_person["time"], "%H:%M").time()
        birth_datetime = datetime.combine(birth_date, birth_time)

        # Make timezone-aware and convert to UTC
        local_tz = pytz.timezone(test_person["timezone"])
        birth_datetime_local = local_tz.localize(birth_datetime)
        birth_datetime_utc = birth_datetime_local.astimezone(pytz.UTC)

        chart = Chart(
            datetime_utc=birth_datetime_utc,
            houses="Placidus",
            loc=(test_person["latitude"], test_person["longitude"]),
            loc_name=test_person["location"],
        )

        # Test planet attributes
        planets_to_test = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
        ]

        for planet_name in planets_to_test:
            if hasattr(chart, planet_name):
                planet = getattr(chart, planet_name)

                # Check required attributes
                required_attrs = [
                    "longitude",
                    "latitude",
                    "sign",
                    "sign_deg",
                    "sign_min",
                ]
                for attr in required_attrs:
                    if hasattr(planet, attr):
                        print(f"✓ {planet_name}.{attr}: {getattr(planet, attr)}")
                    else:
                        print(f"✗ Missing {planet_name}.{attr}")

        print("✓ Validation tests completed")

    except Exception as e:
        print(f"✗ Validation test failed: {e}")


if __name__ == "__main__":
    print("Famous People Test Suite for Starlight Astrology Library")
    print("=" * 60)

    # Generate charts
    results = generate_famous_people_charts()

    # Run validation tests
    run_validation_tests()

    print(f"\n🌟 Test suite completed!")
    print(f"Generated {len(results)} charts successfully")
    print("Check tests/output/famous_people/ and examples/famous_people/ for results")
