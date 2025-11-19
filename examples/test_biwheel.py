#!/usr/bin/env python3
"""
Test script for bi-wheel comparison chart drawing.

Tests the new draw_comparison_chart function with a synastry example.
"""

from datetime import datetime
import datetime as dt

from starlight import ChartBuilder, ComparisonBuilder, draw_comparison_chart
from starlight.core.models import ChartLocation


def test_basic_synastry():
    """Test basic synastry bi-wheel chart."""
    print("Testing basic synastry bi-wheel chart...")

    # Create location
    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    # Person A's birth data
    person_a_native = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Person B's birth data
    person_b = ChartBuilder.from_notable("Marie Curie").calculate()

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(person_a_native, native_label="Albert Einstein")
        .with_partner(person_b, partner_label="Marie Curie")
        .calculate()
    )

    # Draw bi-wheel chart
    draw_comparison_chart(
        synastry,
        filename="examples/chart_examples/biwheel_synastry_basic.svg",
        theme="classic",
        extended_canvas="right",
        show_position_table=True,
        show_aspectarian=True,
    )

    print("✓ Generated: biwheel_synastry_basic.svg")


def test_synastry_themes():
    """Test synastry with different themes."""
    print("\nTesting synastry with different themes...")

    # Get two charts
    chart_a = ChartBuilder.from_notable("Frida Kahlo").calculate()
    chart_b = ChartBuilder.from_notable("Marie Curie").calculate()

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(chart_a, "Frida")
        .with_partner(chart_b, partner_label="Marie")
        .calculate()
    )

    # Dark theme
    draw_comparison_chart(
        synastry,
        filename="examples/chart_examples/biwheel_synastry_dark.svg",
        theme="dark",
        extended_canvas="right",
    )
    print("✓ Generated: biwheel_synastry_dark.svg (dark theme)")

    # Midnight theme
    draw_comparison_chart(
        synastry,
        filename="examples/chart_examples/biwheel_synastry_midnight.svg",
        theme="midnight",
        extended_canvas="right",
    )
    print("✓ Generated: biwheel_synastry_midnight.svg (midnight theme)")


def test_extended_canvas_positions():
    """Test different extended canvas positions."""
    print("\nTesting different extended canvas positions...")

    chart_a = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart_b = ChartBuilder.from_notable("Frida Kahlo").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Einstein")
        .with_partner(chart_b, partner_label="Frida")
        .calculate()
    )

    # Extended canvas on left
    draw_comparison_chart(
        synastry,
        filename="examples/chart_examples/biwheel_extended_left.svg",
        extended_canvas="left",
        theme="classic",
    )
    print("✓ Generated: biwheel_extended_left.svg")

    # Extended canvas below
    draw_comparison_chart(
        synastry,
        filename="examples/chart_examples/biwheel_extended_below.svg",
        extended_canvas="below",
        theme="classic",
    )
    print("✓ Generated: biwheel_extended_below.svg")


if __name__ == "__main__":
    print("=" * 70)
    print("Bi-Wheel Comparison Chart Test Suite")
    print("=" * 70)

    test_basic_synastry()
    test_synastry_themes()
    test_extended_canvas_positions()

    print("\n" + "=" * 70)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 70)
