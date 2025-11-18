"""
Quick test of the new ChartDrawBuilder API.

This tests:
1. ChartDrawBuilder imports correctly
2. Convenience .draw() methods work on CalculatedChart and Comparison
3. Fluent API works
4. Presets work
5. Backwards compatibility (old draw_chart still works)
"""

import sys
from datetime import datetime

# Test imports
try:
    from starlight import ChartBuilder, Native
    from starlight.visualization import ChartDrawBuilder, draw_chart
    print("✅ Imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create a test chart
print("\n📊 Creating test chart...")
native = Native(
    datetime(1994, 1, 6, 11, 47),
    "Palo Alto, CA"
)
chart = ChartBuilder.from_native(native).calculate()
print("✅ Chart created!")

# Test 1: ChartDrawBuilder directly
print("\n🧪 Test 1: ChartDrawBuilder direct usage...")
try:
    builder = ChartDrawBuilder(chart)
    print("✅ ChartDrawBuilder instantiated!")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 2: Convenience .draw() method
print("\n🧪 Test 2: Convenience .draw() method...")
try:
    builder = chart.draw("test_convenience.svg")
    print(f"✅ chart.draw() works! Got: {type(builder).__name__}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 3: Fluent API
print("\n🧪 Test 3: Fluent API chaining...")
try:
    builder = (chart.draw("test_fluent.svg")
        .with_size(800)
        .with_theme("dark")
        .with_moon_phase(position="top-left", show_label=True))
    print(f"✅ Fluent chaining works! Size={builder._size}, Theme={builder._theme}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 4: Presets
print("\n🧪 Test 4: Preset methods...")
try:
    builder_minimal = chart.draw().preset_minimal()
    builder_standard = chart.draw().preset_standard()
    builder_detailed = chart.draw().preset_detailed()
    print(f"✅ All presets work!")
    print(f"   - Minimal: moon_phase={builder_minimal._moon_phase}")
    print(f"   - Standard: moon_phase={builder_standard._moon_phase}")
    print(f"   - Detailed: chart_info={builder_detailed._chart_info}, aspect_counts={builder_detailed._aspect_counts}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 5: Backwards compatibility
print("\n🧪 Test 5: Backwards compatibility (draw_chart still works)...")
try:
    filename = draw_chart(chart, "test_backwards_compat.svg", theme="classic", size=600)
    print(f"✅ draw_chart() still works! Saved to: {filename}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 6: Full save() execution
print("\n🧪 Test 6: Full save() execution...")
try:
    filename = chart.draw("test_full.svg").preset_standard().save()
    print(f"✅ Full execution works! Saved to: {filename}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n\n🎉 ALL TESTS PASSED! 🎉")
print("\nNew API usage examples:")
print("  chart.draw('chart.svg').preset_standard().save()")
print("  chart.draw().with_theme('dark').with_moon_phase(position='top-left').save()")
print("  chart.draw().preset_detailed().with_size(800).save()")
