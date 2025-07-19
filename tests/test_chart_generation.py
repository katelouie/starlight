#!/usr/bin/env python3
"""
Comprehensive test suite for Starlight chart generation functionality.

This consolidates all chart drawing tests into a single file covering:
- Basic wheel geometry and coordinate system
- Planet placement and collision detection  
- Aspect line drawing (including conjunctions)
- Moon phase visualization
- Cache functionality
- Integration with real astronomical data

Run this to test all chart generation components.
"""

import sys
import os
import time
from datetime import datetime
import pytz

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Create output directories
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
CHART_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'charts')
MOON_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'moon_phases')

# Ensure output directories exist
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)
os.makedirs(MOON_OUTPUT_DIR, exist_ok=True)

from starlight.drawing import ChartWheel, draw_chart, draw_moon_phase_standalone


class MockPlanet:
    """Mock planet for testing without Swiss Ephemeris."""
    def __init__(self, name: str, swe_id: int, longitude: float, is_retro: bool = False, 
                 phase_frac: float = None, phase_angle: float = None):
        self.name = name
        self.swe = swe_id
        self.long = longitude
        self.is_retro = is_retro
        self.speed_long = -0.5 if is_retro else 1.0
        
        # Moon phase data (if this is the Moon)
        if name == "Moon":
            self.phase_frac = phase_frac if phase_frac is not None else 0.5
            self.phase_angle = phase_angle if phase_angle is not None else 90.0
            self.phase_para = 0.0  # Parallax
    
    @property
    def has_speed(self) -> bool:
        return True
    
    def aspect(self, other, degrees: int, orb: int):
        """Calculate aspect between this planet and another."""
        distance = abs(self.long - other.long)
        if distance > 180:
            distance = 360 - abs(self.long - other.long)
        
        is_aspect = abs(distance - degrees) <= orb
        aspect_orb = abs(distance - degrees) if is_aspect else None
        
        # Simple movement calculation
        if self.has_speed and other.has_speed:
            if (self.long > other.long) and (self.speed_long < other.speed_long):
                movement = "Applying"
            elif (self.long < other.long) and (self.speed_long > other.speed_long):
                movement = "Applying"
            else:
                movement = "Separating"
        else:
            movement = None
        
        return is_aspect, aspect_orb, distance, movement


class MockAngle:
    """Mock chart angle for testing."""
    def __init__(self, name: str, longitude: float):
        self.name = name
        self.long = longitude


class MockChart:
    """Mock chart with configurable planets and angles."""
    def __init__(self, test_scenario: str = "basic"):
        # House cusps (12 houses, 30° apart)
        self.cusps = [i * 30 for i in range(12)]
        
        # Chart angles
        self.angles = [
            MockAngle("ASC", 0.0),    # 0° Aries
            MockAngle("MC", 270.0),   # 0° Capricorn  
            MockAngle("DSC", 180.0),  # 0° Libra
            MockAngle("IC", 90.0),    # 0° Cancer
        ]
        
        # Objects dict for ASC lookup
        self.objects_dict = {"ASC": self.angles[0]}
        
        # Configure planets based on test scenario
        if test_scenario == "basic":
            self.planets = self._create_basic_planets()
        elif test_scenario == "collision":
            self.planets = self._create_collision_test_planets()
        elif test_scenario == "aspects":
            self.planets = self._create_aspect_test_planets()
        elif test_scenario == "conjunctions":
            self.planets = self._create_conjunction_test_planets()
        elif test_scenario == "moon_phases":
            self.planets = self._create_moon_phase_test_planets()
        else:
            self.planets = self._create_basic_planets()
    
    def _create_basic_planets(self):
        """Basic planet placement for general testing."""
        return [
            MockPlanet("Sun", 0, 45.0),                              # 15° Taurus
            MockPlanet("Moon", 1, 120.0, phase_frac=0.75, phase_angle=45.0), # Waxing gibbous
            MockPlanet("Mercury", 2, 30.0),                          # 0° Taurus
            MockPlanet("Venus", 3, 75.0),                            # 15° Gemini
            MockPlanet("Mars", 4, 200.0, True),                     # 20° Libra (retrograde)
            MockPlanet("Jupiter", 5, 330.0),                         # 0° Pisces
            MockPlanet("Saturn", 6, 270.0),                          # 0° Capricorn
        ]
    
    def _create_collision_test_planets(self):
        """Planets clustered together to test collision detection."""
        return [
            MockPlanet("Sun", 0, 45.0),                              # 15° Taurus
            MockPlanet("Mercury", 2, 46.0),                          # Very close to Sun
            MockPlanet("Venus", 3, 47.0),                            # Very close to Mercury  
            MockPlanet("Moon", 1, 48.0, phase_frac=0.25, phase_angle=135.0), # Waxing crescent
            MockPlanet("Mars", 4, 120.0, True),                     # 0° Leo (retrograde)
            MockPlanet("Jupiter", 5, 121.0),                         # Very close to Mars
            MockPlanet("Saturn", 6, 270.0),                          # 0° Capricorn (isolated)
        ]
    
    def _create_aspect_test_planets(self):
        """Planets positioned to form clear geometric aspects."""
        return [
            MockPlanet("Sun", 0, 0.0),                               # 0° Aries
            MockPlanet("Moon", 1, 120.0, phase_frac=0.5, phase_angle=90.0), # 0° Leo (120° = Trine)
            MockPlanet("Mercury", 2, 90.0),                          # 0° Cancer (90° = Square)
            MockPlanet("Venus", 3, 180.0),                           # 0° Libra (180° = Opposition)
            MockPlanet("Mars", 4, 60.0, True),                      # 0° Gemini (60° = Sextile, retrograde)
            MockPlanet("Jupiter", 5, 240.0),                         # 0° Sagittarius (120° = Trine to Moon)
            MockPlanet("Saturn", 6, 270.0),                          # 0° Capricorn (90° = Square to Moon)
        ]
    
    def _create_conjunction_test_planets(self):
        """Planets positioned to form multiple conjunctions."""
        return [
            # Triple conjunction in Aries
            MockPlanet("Sun", 0, 5.0),                               # 5° Aries
            MockPlanet("Mercury", 2, 7.0),                           # 7° Aries (2° from Sun)
            MockPlanet("Venus", 3, 10.0),                            # 10° Aries (5° from Sun)
            
            # Double conjunction in Leo
            MockPlanet("Mars", 4, 125.0, True),                     # 5° Leo (retrograde)
            MockPlanet("Jupiter", 5, 128.0),                         # 8° Leo (3° from Mars)
            
            # Moon showing phase + other planets
            MockPlanet("Moon", 1, 95.0, phase_frac=0.0, phase_angle=180.0), # New moon
            MockPlanet("Saturn", 6, 270.0),                          # 0° Capricorn (isolated)
        ]
    
    def _create_moon_phase_test_planets(self):
        """Planets with Moon in different phases for testing."""
        return [
            MockPlanet("Sun", 0, 0.0),                               # 0° Aries
            MockPlanet("Moon", 1, 90.0, phase_frac=0.75, phase_angle=45.0), # Waxing gibbous
            MockPlanet("Mercury", 2, 30.0),                          # 0° Taurus
            MockPlanet("Venus", 3, 60.0),                            # 0° Gemini
            MockPlanet("Mars", 4, 180.0),                            # 0° Libra
        ]


def test_coordinate_system():
    """Test the basic coordinate transformation math."""
    print("=" * 60)
    print("TEST 1: Coordinate System")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    
    # Test key astrological positions
    test_points = [
        (0, "Aries point (0°)"),
        (90, "Cancer point (90°)"), 
        (180, "Libra point (180°)"),
        (270, "Capricorn point (270°)")
    ]
    
    print(f"Chart center: ({wheel.center}, {wheel.center})")
    print(f"Outer radius: {wheel.radius_outer}")
    
    for astro_angle, description in test_points:
        x, y = wheel.polar_to_cartesian(astro_angle, wheel.radius_outer)
        print(f"  {description}: SVG coords ({x:.1f}, {y:.1f})")
    
    print("✓ Coordinate system test completed\n")


def test_basic_wheel():
    """Test basic wheel structure without planets."""
    print("=" * 60)
    print("TEST 2: Basic Wheel Structure")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("basic")
    
    # Create SVG with basic elements
    filename = os.path.join(CHART_OUTPUT_DIR, "test_basic_wheel.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    dwg.save()
    
    print(f"✓ Basic wheel SVG created: {filename}")
    print("  - Should show 12 house divisions")
    print("  - Should show zodiac symbols")
    print("  - Should have proper degree tick marks\n")


def test_planet_placement():
    """Test planet placement and retrograde indicators."""
    print("=" * 60)
    print("TEST 3: Planet Placement")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("basic")
    
    # Create SVG with planets
    filename = os.path.join(CHART_OUTPUT_DIR, "test_planets.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    wheel.draw_angles(dwg, mock_chart)
    wheel.draw_planets(dwg, mock_chart)
    dwg.save()
    
    print(f"✓ Planet placement SVG created: {filename}")
    print("  - Should show planets at their positions")
    print("  - Mars should be red (retrograde)")
    print("  - Moon should have phase symbol")
    print("  - Angles (ASC, MC, DSC, IC) should be emphasized")
    
    # Print planet positions
    print("\nPlanet positions:")
    for planet in mock_chart.planets:
        retro_status = "(R)" if planet.is_retro else ""
        phase_info = ""
        if planet.name == "Moon":
            phase_info = f" - {planet.phase_frac:.1%} illuminated"
        print(f"  {planet.name}: {planet.long}° {retro_status}{phase_info}")
    print()


def test_collision_detection():
    """Test collision detection with clustered planets."""
    print("=" * 60)
    print("TEST 4: Collision Detection")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("collision")
    
    # Create SVG with collision detection
    filename = os.path.join(CHART_OUTPUT_DIR, "test_collision.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    wheel.draw_angles(dwg, mock_chart)
    wheel.draw_planets(dwg, mock_chart)
    dwg.save()
    
    print(f"✓ Collision detection SVG created: {filename}")
    print("  - Planets that were too close should be repositioned")
    print("  - Thin lines should connect adjusted planets to actual positions")
    print("  - Mars should still be red (retrograde)")
    
    print("\nClustered planet positions (should trigger collision detection):")
    for planet in mock_chart.planets:
        retro_status = "(R)" if planet.is_retro else ""
        print(f"  {planet.name}: {planet.long}° {retro_status}")
    print()


def test_aspect_drawing():
    """Test aspect line drawing with geometric patterns."""
    print("=" * 60)
    print("TEST 5: Aspect Line Drawing")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("aspects")
    
    # Create SVG with aspects
    filename = os.path.join(CHART_OUTPUT_DIR, "test_aspects.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    wheel.draw_aspects(dwg, mock_chart)
    wheel.draw_angles(dwg, mock_chart)
    wheel.draw_planets(dwg, mock_chart)
    dwg.save()
    
    print(f"✓ Aspect drawing SVG created: {filename}")
    print("  - Should show aspect lines connecting planets")
    print("  - Different colors for different aspect types")
    print("  - Square aspects should be dashed lines")
    print("  - Mars should still be red (retrograde)")
    
    print("\nExpected aspects based on planet positions:")
    print("  Sun (0°) to:")
    print("    - Moon (120°): Trine (blue line)")
    print("    - Mercury (90°): Square (orange dashed line)")
    print("    - Venus (180°): Opposition (red line)")
    print("    - Mars (60°): Sextile (green line)")
    print("  Moon (120°) to:")
    print("    - Jupiter (240°): Trine (blue line)")
    print("    - Saturn (270°): Square (orange dashed line)")
    print()


def test_conjunction_arcs():
    """Test conjunction arc drawing."""
    print("=" * 60)
    print("TEST 6: Conjunction Arc Drawing")
    print("=" * 60)
    
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("conjunctions")
    
    # Create SVG with conjunction arcs
    filename = os.path.join(CHART_OUTPUT_DIR, "test_conjunctions.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    wheel.draw_aspects(dwg, mock_chart)
    wheel.draw_angles(dwg, mock_chart)
    wheel.draw_planets(dwg, mock_chart)
    dwg.save()
    
    print(f"✓ Conjunction arc SVG created: {filename}")
    print("  - Should show curved arc lines for conjunctions")
    print("  - Triple conjunction: Sun-Mercury-Venus in Aries")
    print("  - Double conjunction: Mars-Jupiter in Leo")
    print("  - Mars should still be red (retrograde)")
    print("  - Moon should show new moon phase")
    
    print("\nExpected conjunctions:")
    print("  - Sun (5°) ∽ Mercury (7°): 2° orb")
    print("  - Sun (5°) ∽ Venus (10°): 5° orb")
    print("  - Mercury (7°) ∽ Venus (10°): 3° orb")
    print("  - Mars (125°) ∽ Jupiter (128°): 3° orb")
    print()


def test_moon_phases():
    """Test moon phase visualization."""
    print("=" * 60)
    print("TEST 7: Moon Phase Visualization")
    print("=" * 60)
    
    # Test standalone moon phase function
    phases = [
        (0.0, True, "new_moon_test.svg", "New Moon"),
        (0.25, True, "waxing_crescent_test.svg", "Waxing Crescent"), 
        (0.5, True, "first_quarter_test.svg", "First Quarter"),
        (0.75, True, "waxing_gibbous_test.svg", "Waxing Gibbous"),
        (1.0, True, "full_moon_test.svg", "Full Moon"),
        (0.75, False, "waning_gibbous_test.svg", "Waning Gibbous"),
        (0.5, False, "third_quarter_test.svg", "Third Quarter"),
        (0.25, False, "waning_crescent_test.svg", "Waning Crescent")
    ]
    
    print("Creating standalone moon phase demonstrations...")
    for fraction, waxing, filename, phase_name in phases:
        filepath = os.path.join(MOON_OUTPUT_DIR, filename)
        draw_moon_phase_standalone(fraction, waxing, filepath, 100)
        print(f"  ✓ Created {filepath} - {phase_name}")
    
    # Test moon phase in chart context
    wheel = ChartWheel(size=600)
    mock_chart = MockChart("moon_phases")
    
    filename = os.path.join(CHART_OUTPUT_DIR, "test_moon_in_chart.svg")
    dwg = wheel.create_svg(filename)
    wheel.draw_house_divisions(dwg, mock_chart)
    wheel.draw_zodiac_ring(dwg, mock_chart)
    wheel.draw_angles(dwg, mock_chart)
    wheel.draw_planets(dwg, mock_chart)  # Moon should show phase
    dwg.save()
    
    print(f"  ✓ Created {filename} - Chart with moon phase")
    print("\nMoon phase visualization system ready!")
    print("✓ All moon phases created as individual SVGs")
    print("✓ Moon phase integrated into chart display\n")


def test_cache_functionality():
    """Test caching with real Chart objects (requires Swiss Ephemeris)."""
    print("=" * 60)
    print("TEST 8: Cache Functionality (Optional)")
    print("=" * 60)
    
    try:
        from starlight.chart import Chart
        from starlight.cache import cache_info, clear_cache
        
        print("Testing cache functionality...")
        
        # Clear any existing cache
        clear_cache()
        
        # Create test datetime
        dt_utc = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
        
        # Test 1: Create a chart - this should populate cache
        print("1. Creating first chart (should populate cache)...")
        start_time = time.time()
        chart1 = Chart(
            datetime_utc=dt_utc,
            loc_name="San Francisco, CA",
            houses='Placidus'
        )
        first_time = time.time() - start_time
        print(f"   First chart creation took: {first_time:.2f} seconds")
        
        # Check cache info
        info = cache_info()
        print(f"   Cache now has {info['total_cached_files']} files")
        
        # Test 2: Create same chart again - this should use cache
        print("2. Creating identical chart (should use cache)...")
        start_time = time.time()
        chart2 = Chart(
            datetime_utc=dt_utc,
            loc_name="San Francisco, CA",
            houses='Placidus'
        )
        second_time = time.time() - start_time
        print(f"   Second chart creation took: {second_time:.2f} seconds")
        
        # Performance improvement check
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"   ✓ Cache improved performance by {improvement:.1f}%")
        
        # Test with real chart drawing
        print("3. Testing chart drawing with real data...")
        real_chart_path = os.path.join(CHART_OUTPUT_DIR, "test_real_chart.svg")
        chart_filename = draw_chart(chart1, real_chart_path, 600)
        print(f"   ✓ Real chart created: {chart_filename}")
        print(f"   Chart contains {len(chart1.planets)} planets and {len(chart1.angles)} angles")
        
        print("✓ Cache functionality tests completed\n")
        
    except ImportError as e:
        print(f"⚠ Cache test skipped - missing dependencies: {e}")
        print("  This is expected if Swiss Ephemeris or other dependencies are missing\n")
    except Exception as e:
        print(f"⚠ Cache test failed: {e}")
        print("  This may be expected if Swiss Ephemeris data is not available\n")


def demo_moon_phases():
    """
    Create a demonstration showing different moon phases.
    """
    phases = [
        (0.0, True, "new_moon.svg", "New Moon"),
        (0.25, True, "waxing_crescent.svg", "Waxing Crescent"), 
        (0.5, True, "first_quarter.svg", "First Quarter"),
        (0.75, True, "waxing_gibbous.svg", "Waxing Gibbous"),
        (1.0, True, "full_moon.svg", "Full Moon"),
        (0.75, False, "waning_gibbous.svg", "Waning Gibbous"),
        (0.5, False, "third_quarter.svg", "Third Quarter"),
        (0.25, False, "waning_crescent.svg", "Waning Crescent")
    ]
    
    print("Creating moon phase demonstration files...")
    for fraction, waxing, filename, phase_name in phases:
        filepath = os.path.join(MOON_OUTPUT_DIR, filename)
        draw_moon_phase_standalone(fraction, waxing, filepath, 120)
        print(f"Created {filepath} - {phase_name} ({fraction:.1%} illuminated)")
    
    print("\nMoon phase visualization system ready!")
    print("You can generate individual moon phases using draw_moon_phase_standalone()")
    print("You can customize styling by modifying the moon_style dict in _create_moon_phase_symbol")


def run_all_tests():
    """Run the complete test suite."""
    print("STARLIGHT CHART GENERATION TEST SUITE")
    print("=====================================")
    print(f"Testing all chart generation components...\n")
    
    start_time = time.time()
    
    # Run all tests
    test_coordinate_system()
    test_basic_wheel() 
    test_planet_placement()
    test_collision_detection()
    test_aspect_drawing()
    test_conjunction_arcs()
    test_moon_phases()
    test_cache_functionality()
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ All chart generation tests completed!")
    print(f"⏱ Total test time: {total_time:.2f} seconds")
    print("\nGenerated test files:")
    print(f"Chart outputs (in {CHART_OUTPUT_DIR}):")
    print("  - test_basic_wheel.svg (wheel structure)")
    print("  - test_planets.svg (planet placement)")
    print("  - test_collision.svg (collision detection)")
    print("  - test_aspects.svg (aspect lines)")
    print("  - test_conjunctions.svg (conjunction arcs)")
    print("  - test_moon_in_chart.svg (moon in chart)")
    print("  - test_real_chart.svg (if cache test succeeded)")
    print(f"\nMoon phase outputs (in {MOON_OUTPUT_DIR}):")
    print("  - 8x moon phase SVGs (all phases)")
    print("\nOpen these SVG files in a web browser to view the results!")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "moon":
            demo_moon_phases()
        else:
            run_all_tests()
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)