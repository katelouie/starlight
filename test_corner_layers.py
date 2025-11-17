#!/usr/bin/env python3
"""
Test script for new corner layer features.

Tests:
1. Aspect counts layer
2. Element/modality cross-table layer
3. Chart shape detection layer
4. All corners occupied with auto-padding
"""

from starlight import ChartBuilder, draw_chart


def test_individual_corners():
    """Test each corner layer individually."""
    print("Testing individual corner layers...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 1: Aspect counts only
    draw_chart(
        chart,
        filename="examples/chart_examples/test_aspect_counts.svg",
        moon_phase=False,
        aspect_counts=True,
        aspect_counts_position="top-right",
    )
    print("✓ Generated: test_aspect_counts.svg")

    # Test 2: Element/modality table only
    draw_chart(
        chart,
        filename="examples/chart_examples/test_element_modality.svg",
        moon_phase=False,
        element_modality_table=True,
        element_modality_position="bottom-left",
    )
    print("✓ Generated: test_element_modality.svg")

    # Test 3: Chart shape only
    draw_chart(
        chart,
        filename="examples/chart_examples/test_chart_shape.svg",
        moon_phase=False,
        chart_shape=True,
        chart_shape_position="bottom-right",
    )
    print("✓ Generated: test_chart_shape.svg")


def test_multiple_corners():
    """Test multiple corner layers at once."""
    print("\nTesting multiple corner layers...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 4: All four corners occupied
    draw_chart(
        chart,
        filename="examples/chart_examples/test_all_four_corners.svg",
        moon_phase=True,
        moon_phase_position="center",  # Keep moon in center
        chart_info=True,
        chart_info_position="top-left",
        aspect_counts=True,
        aspect_counts_position="top-right",
        element_modality_table=True,
        element_modality_position="bottom-left",
        chart_shape=True,
        chart_shape_position="bottom-right",
        auto_padding=True,  # Should apply padding
    )
    print("✓ Generated: test_all_four_corners.svg (with auto-padding)")

    # Test 5: All corners + moon in corner
    draw_chart(
        chart,
        filename="examples/chart_examples/test_all_corners_moon_aside.svg",
        moon_phase=True,
        moon_phase_position="top-right",
        moon_phase_label=True,
        chart_info=True,
        chart_info_position="top-left",
        aspect_counts=False,  # Skip aspect counts to make room for moon
        element_modality_table=True,
        element_modality_position="bottom-left",
        chart_shape=True,
        chart_shape_position="bottom-right",
        auto_padding=True,
    )
    print("✓ Generated: test_all_corners_moon_aside.svg")


def test_themed_corners():
    """Test corner layers with different themes."""
    print("\nTesting corner layers with themes...")

    chart = ChartBuilder.from_notable("Marie Curie").calculate()

    # Test 6: Dark theme with all corners
    draw_chart(
        chart,
        filename="examples/chart_examples/test_dark_all_corners.svg",
        theme="dark",
        moon_phase=True,
        moon_phase_position="center",
        chart_info=True,
        chart_info_position="top-left",
        aspect_counts=True,
        aspect_counts_position="top-right",
        element_modality_table=True,
        element_modality_position="bottom-left",
        chart_shape=True,
        chart_shape_position="bottom-right",
    )
    print("✓ Generated: test_dark_all_corners.svg (dark theme)")

    # Test 7: Midnight theme with all corners
    draw_chart(
        chart,
        filename="examples/chart_examples/test_midnight_all_corners.svg",
        theme="midnight",
        moon_phase=False,
        chart_info=True,
        chart_info_position="top-left",
        aspect_counts=True,
        aspect_counts_position="top-right",
        element_modality_table=True,
        element_modality_position="bottom-left",
        chart_shape=True,
        chart_shape_position="bottom-right",
    )
    print("✓ Generated: test_midnight_all_corners.svg (midnight theme)")


def test_different_chart_shapes():
    """Test chart shape detection with different notables."""
    print("\nTesting chart shape detection on various charts...")

    notables = [
        "Albert Einstein",
        "Marie Curie",
        "Leonardo da Vinci",
        "Frida Kahlo",
        "Wolfgang Amadeus Mozart",
    ]

    for notable in notables:
        try:
            chart = ChartBuilder.from_notable(notable).calculate()
            filename = f"examples/chart_examples/shape_{notable.replace(' ', '_').lower()}.svg"

            draw_chart(
                chart,
                filename=filename,
                moon_phase=False,
                chart_info=True,
                chart_info_position="top-left",
                chart_info_fields=["name"],
                chart_shape=True,
                chart_shape_position="bottom-right",
            )
            print(f"✓ Generated: {filename}")
        except Exception as e:
            print(f"✗ Skipped {notable}: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("Corner Layers Test Suite")
    print("=" * 70)

    test_individual_corners()
    test_multiple_corners()
    test_themed_corners()
    test_different_chart_shapes()

    print("\n" + "=" * 70)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 70)
