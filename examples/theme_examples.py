"""
Example: Chart Themes

This example demonstrates the different visual themes available for
chart rendering.

Each theme provides a cohesive visual style including:
- Background and border colors
- Zodiac ring styling
- House, angle, and planet colors
- Aspect line colors
- Default zodiac palette (can be overridden)
"""

from datetime import datetime

from starlight import ChartBuilder, draw_chart
from starlight.visualization import ChartTheme
from starlight.visualization.themes import get_theme_description

# Create a sample chart (Kate Louie's birth data)
chart = ChartBuilder.from_native(
    datetime(1994, 1, 6, 11, 47), "Palo Alto, CA"
).calculate()

print("Generating charts with different themes...\n")

# Generate chart for each theme
for theme in ChartTheme:
    filename = f"examples/chart_examples/theme_{theme.value}.svg"
    description = get_theme_description(theme)

    # Draw chart with theme (uses theme's default zodiac palette)
    draw_chart(chart, filename=filename, theme=theme)

    print(f"✓ {description}")
    print(f"  → {filename}\n")

print("\nAll theme charts generated successfully!")

# ============================================================================
# Advanced: Custom combinations of theme + palette
# ============================================================================

print("\n" + "=" * 70)
print("Advanced Examples: Themes with Custom Palettes")
print("=" * 70 + "\n")

# Example 1: Dark theme with rainbow zodiac
draw_chart(
    chart,
    filename="examples/chart_examples/dark_rainbow.svg",
    theme="dark",
    zodiac_palette="rainbow",
)
print("✓ Dark theme + Rainbow palette → dark_rainbow.svg")

# Example 2: Midnight theme with elemental zodiac
draw_chart(
    chart,
    filename="examples/chart_examples/midnight_elemental.svg",
    theme="midnight",
    zodiac_palette="elemental",
)
print("✓ Midnight theme + Elemental palette → midnight_elemental.svg")

# Example 3: Neon theme (already uses rainbow by default, but let's try elemental)
draw_chart(
    chart,
    filename="examples/chart_examples/neon_elemental.svg",
    theme="neon",
    zodiac_palette="elemental",
)
print("✓ Neon theme + Elemental palette → neon_elemental.svg")

# Example 4: Theme with custom style overrides
draw_chart(
    chart,
    filename="examples/chart_examples/custom_styled.svg",
    theme="celestial",
    zodiac_palette="rainbow",
    style_config={
        "planets": {
            "glyph_color": "#FFFFFF",  # Override planet color to pure white
            "glyph_size": "36px",  # Make planets larger
        }
    },
)
print("✓ Celestial theme + Rainbow palette + Custom styles → custom_styled.svg")

print("\nDone! Check examples/chart_examples/ for all generated charts.")

# ============================================================================
# Theme Reference Guide
# ============================================================================

print("\n" + "=" * 70)
print("Theme Reference")
print("=" * 70 + "\n")

print("CLASSIC - Professional grey/neutral (default)")
print("  • Best for: Professional reports, printing")
print("  • Default palette: Grey")
print()

print("DARK - Dark grey background with light text")
print("  • Best for: Dark mode UIs, screens")
print("  • Default palette: Grey")
print()

print("MIDNIGHT - Elegant night sky with deep navy and white/gold")
print("  • Best for: Beautiful presentations, romantic aesthetic")
print("  • Default palette: Grey (light colors)")
print()

print("NEON - Cyberpunk aesthetic with bright neon colors")
print("  • Best for: Fun, modern, attention-grabbing")
print("  • Default palette: Rainbow (neon version)")
print()

print("SEPIA - Vintage aged paper with warm browns")
print("  • Best for: Historical charts, classical feel")
print("  • Default palette: Grey (brown tones)")
print()

print("PASTEL - Soft gentle colors, light and airy")
print("  • Best for: Gentle aesthetic, wellness contexts")
print("  • Default palette: Rainbow (pastel version)")
print()

print("CELESTIAL - Cosmic galaxy with deep purples and gold")
print("  • Best for: Mystical, spiritual contexts")
print("  • Default palette: Grey (purple/gold tones)")
