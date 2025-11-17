#!/usr/bin/env python3
"""
Test script for new chart info and moon phase positioning features.

Tests:
1. Moon phase in different positions
2. Moon phase with label
3. Chart info in different corners
4. Combined moon phase and chart info
"""

from datetime import datetime
from starlight import ChartBuilder, draw_chart


def test_moon_positions():
    """Test moon phase in different positions."""
    print("Testing moon phase positions...")

    # Use a notable chart to avoid geocoding issues
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 1: Moon in center (default)
    draw_chart(
        chart,
        filename="examples/chart_examples/moon_center.svg",
        moon_phase=True,
        moon_phase_position="center",
        moon_phase_label=False,
    )
    print("✓ Generated: moon_center.svg")

    # Test 2: Moon in top-right with label
    draw_chart(
        chart,
        filename="examples/chart_examples/moon_top_right_labeled.svg",
        moon_phase=True,
        moon_phase_position="top-right",
        moon_phase_label=True,
    )
    print("✓ Generated: moon_top_right_labeled.svg")

    # Test 3: Moon in bottom-left with label
    draw_chart(
        chart,
        filename="examples/chart_examples/moon_bottom_left_labeled.svg",
        moon_phase=True,
        moon_phase_position="bottom-left",
        moon_phase_label=True,
    )
    print("✓ Generated: moon_bottom_left_labeled.svg")


def test_chart_info():
    """Test chart info display."""
    print("\nTesting chart info display...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 4: Chart info in top-left
    draw_chart(
        chart,
        filename="examples/chart_examples/chart_info_top_left.svg",
        moon_phase=False,
        chart_info=True,
        chart_info_position="top-left",
    )
    print("✓ Generated: chart_info_top_left.svg")

    # Test 5: Chart info in top-right
    draw_chart(
        chart,
        filename="examples/chart_examples/chart_info_top_right.svg",
        moon_phase=False,
        chart_info=True,
        chart_info_position="top-right",
    )
    print("✓ Generated: chart_info_top_right.svg")


def test_combined():
    """Test combined moon phase and chart info."""
    print("\nTesting combined features...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 6: Moon in bottom-right, chart info in top-left
    draw_chart(
        chart,
        filename="examples/chart_examples/combined_moon_and_info.svg",
        moon_phase=True,
        moon_phase_position="bottom-right",
        moon_phase_label=True,
        chart_info=True,
        chart_info_position="top-left",
    )
    print("✓ Generated: combined_moon_and_info.svg")

    # Test 7: Moon in top-right, chart info in top-left (showing full aspect lines)
    draw_chart(
        chart,
        filename="examples/chart_examples/moon_corner_full_aspects.svg",
        moon_phase=True,
        moon_phase_position="top-right",
        moon_phase_label=True,
        chart_info=True,
        chart_info_position="top-left",
        theme="dark",
    )
    print("✓ Generated: moon_corner_full_aspects.svg (with dark theme)")


def test_notable():
    """Test with a notable chart."""
    print("\nTesting with notable (Albert Einstein)...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 8: Full-featured chart with notable
    draw_chart(
        chart,
        filename="examples/chart_examples/einstein_full_featured.svg",
        moon_phase=True,
        moon_phase_position="bottom-right",
        moon_phase_label=True,
        chart_info=True,
        chart_info_position="top-left",
        chart_info_fields=["name", "location", "datetime", "coordinates"],
        theme="midnight",
    )
    print("✓ Generated: einstein_full_featured.svg")


if __name__ == "__main__":
    print("=" * 60)
    print("Chart Info & Moon Phase Positioning Test Suite")
    print("=" * 60)

    test_moon_positions()
    test_chart_info()
    test_combined()
    test_notable()

    print("\n" + "=" * 60)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 60)
