#!/usr/bin/env python3
"""
Test script for extended canvas features.

Tests:
1. Position table on right
2. Aspectarian on right
3. Both tables on right
4. Tables below chart
5. Tables on left
6. Extended canvas with different themes
"""

from starlight import ChartBuilder, draw_chart


def test_extended_right():
    """Test extended canvas to the right."""
    print("Testing extended canvas (right)...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    draw_chart(
        chart,
        filename="examples/chart_examples/extended_right.svg",
        extended_canvas="right",
        show_position_table=True,
        show_aspectarian=True,
        moon_phase=False,
    )
    print("✓ Generated: extended_right.svg")


def test_extended_left():
    """Test extended canvas to the left."""
    print("\nTesting extended canvas (left)...")

    chart = ChartBuilder.from_notable("Marie Curie").calculate()

    draw_chart(
        chart,
        filename="examples/chart_examples/extended_left.svg",
        extended_canvas="left",
        show_position_table=True,
        show_aspectarian=True,
        moon_phase=False,
    )
    print("✓ Generated: extended_left.svg")


def test_extended_below():
    """Test extended canvas below."""
    print("\nTesting extended canvas (below)...")

    chart = ChartBuilder.from_notable("Frida Kahlo").calculate()

    draw_chart(
        chart,
        filename="examples/chart_examples/extended_below.svg",
        extended_canvas="below",
        show_position_table=True,
        show_aspectarian=True,
        moon_phase=False,
    )
    print("✓ Generated: extended_below.svg")


def test_extended_with_themes():
    """Test extended canvas with different themes."""
    print("\nTesting extended canvas with themes...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Dark theme
    draw_chart(
        chart,
        filename="examples/chart_examples/extended_dark.svg",
        extended_canvas="right",
        show_position_table=True,
        show_aspectarian=True,
        theme="dark",
        moon_phase=False,
    )
    print("✓ Generated: extended_dark.svg (dark theme)")

    # Midnight theme
    draw_chart(
        chart,
        filename="examples/chart_examples/extended_midnight.svg",
        extended_canvas="right",
        show_position_table=True,
        show_aspectarian=True,
        theme="midnight",
        moon_phase=False,
    )
    print("✓ Generated: extended_midnight.svg (midnight theme)")


def test_extended_with_corners():
    """Test extended canvas combined with corner info."""
    print("\nTesting extended canvas with corner info...")

    chart = ChartBuilder.from_notable("Marie Curie").calculate()

    draw_chart(
        chart,
        filename="examples/chart_examples/extended_full_featured.svg",
        extended_canvas="right",
        show_position_table=True,
        show_aspectarian=True,
        chart_info=True,
        chart_info_position="top-left",
        aspect_counts=True,
        aspect_counts_position="top-right",
        element_modality_table=True,
        element_modality_position="bottom-left",
        chart_shape=True,
        chart_shape_position="bottom-right",
        moon_phase=True,
        moon_phase_position="center",
    )
    print("✓ Generated: extended_full_featured.svg (all features)")


if __name__ == "__main__":
    print("=" * 70)
    print("Extended Canvas Test Suite")
    print("=" * 70)

    test_extended_right()
    test_extended_left()
    test_extended_below()
    test_extended_with_themes()
    test_extended_with_corners()

    print("\n" + "=" * 70)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 70)
